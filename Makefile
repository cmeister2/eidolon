WORKING_DIR := ./working
DOCKER_TAG ?= eidolon
DATA_SOURCE ?= global

# Build target for the docker image
build_eidolon:
	@docker build --build-arg DATA_SOURCE=$(DATA_SOURCE) -t $(DOCKER_TAG) .
	@echo Built docker image $(DOCKER_TAG)

use_gb_sql: ./data/publicdns_gb.sql
	@cat $< | sqlite3 $(WORKING_DIR)/resolvers.db

# Runs eidolon, mapping localhost port 53 to the docker container.
run_eidolon:
	@docker run --rm -d -p 127.0.0.1:53:5353/udp $(DOCKER_TAG)
