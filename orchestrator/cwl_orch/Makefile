ORCHPATH := $(realpath ..)

venv:
	uv venv

check-venv:
	@if [ ! -d .venv ]; then \
		make venv; \
	fi

install: check-venv
	uv pip install cwltool

create-mockchecker-context:
	cd ../../barebone && uv run src/mki_barebone/main.py -i ${ORCHPATH}/tests/nodes/mockchecker/ -o ${ORCHPATH}/tests/nodes/mockchecker/tests/context

create-mockmodel-context:
	cd ../../barebone && uv run src/mki_barebone/main.py -i ${ORCHPATH}/tests/nodes/mockmodel/ -o ${ORCHPATH}/tests/nodes/mockmodel/tests/context

run-mock-workflow: check-venv
	uv run cwltool --outdir ../tests/data ../tests/workflows/mockworkflow/cwl/workflow.cwl ../tests/workflows/mockworkflow/cwl/job.json

run-scikit-workflow: check-venv
	uv run cwltool --outdir ../tests/data ../tests/workflows/scikit-workflow/cwl/workflow.cwl ../tests/workflows/scikit-workflow/cwl/job.json