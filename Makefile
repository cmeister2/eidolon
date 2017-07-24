dev_docker:
	@docker build -t eidolon -f eidolon.dockerfile .

run_docker:
	@docker run -it -v $(PWD):/eidolon -w /eidolon eidolon bash

docker_unbound:
	@docker run -it -v $(PWD):/eidolon -w /eidolon eidolon make compile_unbound

compile_unbound:
	@./unbound.sh
