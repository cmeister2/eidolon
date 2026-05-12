"""Shared test fixtures."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_csv() -> str:
    """Load the sample CSV fixture as a string."""
    return (FIXTURES_DIR / "sample.csv").read_text()
