ifeq ($(IMGNAME),)
IMGNAME := mock-orch
endif
ifeq ($(TAG),)
TAG := latest
endif

netname = mock-pipeline-net
builder-name = barebone-builder
builder-sha = sha256:c5137fdd77377ea102a2622714df55459fe42e5867ba180bda07291aa7952d9b
source_date_epoch = 1742214363
container_template_dir = ../../src/mki_barebone/templates/src/container
uid = $(shell id -u)

proto:
	rm src/orchestrator/grpc_backend/module_pb2_grpc.py src/orchestrator/grpc_backend/module_pb2.py || true
	cd src/orchestrator && uv run python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. grpc_backend/module.proto

check-builder:
	@if ! docker buildx inspect $(builder-name) 2>/dev/null | grep -q $(builder-sha); then \
		make builder; \
	fi

builder:
	@if docker buildx ls 2>/dev/null | grep -q $(builder-name); then \
		docker buildx rm $(builder-name); \
	fi
	docker buildx create --name $(builder-name) --driver=docker-container --driver-opt=image=moby/buildkit@$(builder-sha) --use --bootstrap

docker: check-builder
	SOURCE_DATE_EPOCH=$(source_date_epoch) docker buildx build $(ADDBUILDARGS) --builder $(builder-name) --build-arg SOURCE_DATE_EPOCH=$(source_date_epoch) --output type=docker,rewrite-timestamp=true -t $(IMGNAME):$(TAG) --build-arg UID=$(uid) .

run:
	docker rm --force $(IMGNAME) || true
	docker network create --driver bridge $(netname) || true
	docker run --rm --name $(IMGNAME) $(ADDARGS) --network $(netname) -ti $(IMGNAME):$(TAG)

test-reproducibility:
	TAG=v1 ADDBUILDARGS=--no-cache make docker 
	TAG=v2 ADDBUILDARGS=--no-cache make docker 
	~/go/bin/diffoci diff docker://$(IMGNAME):v1 docker://$(IMGNAME):v2 > diff.txt