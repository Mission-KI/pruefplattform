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

sync-extra:
	cp -rf extra tests/nodes/mocktool

create-mockcontainer: check-venv sync-extra
	uv run src/mki_barebone/main.py -i tests/nodes/mocktool -o tests/nodes/mocktool/tests/context/args

create-mockcontainer-grpc: check-venv sync-extra
	uv run src/mki_barebone/main.py -i tests/nodes/mocktool -o tests/nodes/mocktool/tests/context/grpc --interface grpc

test: install-dev
	uv run pytest -m unit

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

.test-reproducibility:
	cd tests/mockcontainer && make .test-reproducibility
	
docs: check-venv install-dev
	uv run pdoc --html --force --output-dir docs src/mki_barebone
	uv run pdoc --html --force --output-dir docs extra/mki-barebone-io/src/mki_barebone_io
	uv run pdoc --html --force --output-dir docs tests
