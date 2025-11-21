name = scikit-metrics-tool-grpc
ifeq ($(TAG),)
TAG := latest
endif

netname = scikit-metrics-tool-grpc-net
builder-name = barebone-builder
builder-sha = sha256:c5137fdd77377ea102a2622714df55459fe42e5867ba180bda07291aa7952d9b
source_date_epoch = 1742214363

ifeq ($(BUILD_UID),)
BUILD_UID := $(shell id -u)
endif

ifeq ($(GO_BINARY),)
GO_BINARY := go
endif

ifeq ($(DIFFOCI_BINARY),)
DIFFOCI_BINARY := diffoci
endif

proto:
	rm src/enpkg/grpc_backend/module_pb2_grpc.py src/enpkg/grpc_backend/module_pb2.py || true
	cd src/enpkg && uv run python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. grpc_backend/module.proto

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
	SOURCE_DATE_EPOCH=$(source_date_epoch) docker buildx build $(ADDBUILDARGS) --builder $(builder-name) --build-arg SOURCE_DATE_EPOCH=$(source_date_epoch) --output type=docker,rewrite-timestamp=true -t $(name):$(TAG) --build-arg UID=$(BUILD_UID) .
