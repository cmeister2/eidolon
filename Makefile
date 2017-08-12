# Make the eidolon development environment in docker
eidolon_dev:
	@docker build -t eidolon_dev -f eidolon-dev.dockerfile .

# Run the eidolon development environment
run_eidolon_dev:
	@docker run -it -v $(PWD):/eidolon -w /eidolon cmeister2/eidolon_dev bash

# Compile unbound inside the development environment
docker_unbound:
	@docker run \
		-it \
		-v $(PWD):/eidolon \
		-w /eidolon \
		cmeister2/eidolon_dev \
		make compile_unbound

# A make target for compiling unbound inside the development environment
compile_unbound:
	@./unbound.sh
