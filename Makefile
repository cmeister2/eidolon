WORKING_DIR := ./working
DOCKER_TAG ?= eidolon

# Build target for the docker image
build_eidolon: $(WORKING_DIR)/nginx.conf
	@docker build -t $(DOCKER_TAG) -f eidolon.dockerfile .

$(WORKING_DIR)/nginx.conf: $(WORKING_DIR)/resolvers.db
	@./python/generate_nginx_conf.py --database $< --outputfile $@

use_gb_sql: ./data/publicdns_gb.sql
	@cat $< | sqlite3 $(WORKING_DIR)/resolvers.db

# Runs eidolon, mapping localhost port 53 to the docker container.
run_eidolon:
	@docker run --rm -d -p 127.0.0.1:53:5353/udp $(DOCKER_TAG)
