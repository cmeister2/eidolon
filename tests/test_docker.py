"""Integration tests that build and query a live Docker container."""

import random
import shutil
import subprocess
import time
from collections.abc import Generator

import pytest

pytestmark = pytest.mark.docker

DOCKER = shutil.which("docker")
DIG = shutil.which("dig")


def _docker_available() -> bool:
    """Check whether the Docker daemon is reachable."""
    if DOCKER is None:
        return False
    try:
        subprocess.run(
            [DOCKER, "info"],
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return False
    return True


skip_no_docker = pytest.mark.skipif(
    not _docker_available(), reason="Docker not available"
)
skip_no_dig = pytest.mark.skipif(DIG is None, reason="dig not installed")

IMAGE_NAME = "eidolon-integration-test"


@pytest.fixture(scope="module")
def container_port() -> Generator[int, None, None]:
    """Build the image, start a container on a random port, yield it, then clean up."""
    assert DOCKER is not None

    subprocess.run(
        ["eidolon", "--tag", "global", "--output", "nginx.conf"],
        check=True,
        timeout=120,
    )

    subprocess.run(
        [DOCKER, "build", "-t", IMAGE_NAME, "."],
        check=True,
        timeout=300,
    )

    port = random.randint(10000, 60000)
    container_id = subprocess.run(
        [
            DOCKER,
            "run",
            "--rm",
            "-d",
            "-p",
            f"127.0.0.1:{port}:5353/udp",
            IMAGE_NAME,
        ],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()

    # Wait for nginx to be ready
    for _ in range(20):
        result = subprocess.run(
            [DOCKER, "inspect", "-f", "{{.State.Running}}", container_id],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip() == "true":
            break
        time.sleep(0.5)
    else:
        subprocess.run([DOCKER, "stop", container_id], capture_output=True)
        pytest.fail("Container did not start in time")

    # Brief pause for nginx to bind
    time.sleep(1)

    yield port

    subprocess.run([DOCKER, "stop", container_id], capture_output=True, timeout=30)


def _dig(
    port: int, domain: str, record_type: str = "A"
) -> subprocess.CompletedProcess[str]:
    """Run a dig query against the container."""
    assert DIG is not None
    return subprocess.run(
        [
            DIG,
            "@127.0.0.1",
            "-p",
            str(port),
            domain,
            record_type,
            "+time=2",
            "+tries=1",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _dig_with_retry(port: int, domain: str, retries: int = 10) -> bool:
    """Try resolving a domain multiple times, succeeding if any attempt works.

    With a round-robin of public resolvers, some upstreams may be unresponsive.
    Each retry hits a different upstream.
    """
    for _ in range(retries):
        result = _dig(port, domain, "A")
        if result.returncode == 0 and "ANSWER SECTION" in result.stdout:
            return True
    return False


@skip_no_docker
@skip_no_dig
def test_resolves_a_record(container_port: int) -> None:
    """The container should resolve an A record for google.com."""
    assert _dig_with_retry(container_port, "google.com"), "Failed to resolve A record"


@skip_no_docker
@skip_no_dig
def test_resolves_txt_record(container_port: int) -> None:
    """The container should resolve a TXT record for google.com."""
    for _ in range(5):
        result = _dig(container_port, "google.com", "TXT")
        if result.returncode == 0 and "ANSWER SECTION" in result.stdout:
            return
    pytest.fail("Failed to resolve TXT record after retries")
