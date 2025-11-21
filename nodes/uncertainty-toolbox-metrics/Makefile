venv:
	uv venv

check-venv:
	@if [ ! -d .venv ]; then \
		make venv; \
	fi

install: check-venv
	uv pip install .

install-dev: check-venv
	uv pip install .[dev]

test-unit: install-dev
	uv run pytest -m unit

test-integration: install-dev
	uv run pytest -m "integration and cwl"

test-integration-grpc: install-dev
	uv run pytest -m "integration and grpc"

test-integration-all: install-dev
	uv run pytest -m integration

test-barebone: install-dev
	uv run pytest -m "barebone and cwl"

test-barebone-grpc: install-dev
	uv run pytest -m "barebone and grpc"

test-barebone-all: install-dev
	uv run pytest -m barebone

test-all: install-dev
	uv run pytest