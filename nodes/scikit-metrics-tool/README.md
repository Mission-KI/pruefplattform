# scikit-metrics-tool

A tool for computing common performance metrics for classification and regression models build using the scikit-learn library

This tool has been build by the MKI barebone build tool

## Project structure

- tests: Test scripts for the image context build via the barebone build tool
- .gitignore: Files not to commit/push
- src: Source code containing the package "scikit_metrics" with tool wrapper functions
- Makefile: Build file
- README.md: this readme 
- pyproject.toml: python package specification including requirements
- uv.lock: A lockfile created by `uv` for better reproducibility of the python environment and dependencies

## Installation

### Linux shell on windows with wsl

- We are developing mostly in a linux environment / with linux tool, it is recommended to install WSL2 under windows
- In powershell use ``wsl -d <DISTRO>``, e.g. ``wsl -d Ubuntu``, to access a linux shell under windows
- Use can use `git`, `docker`, `make` etc. as expected in the linux shell
- Also you can activate python virtual environments using `source <name>/bin/activate`

### Installation of uv/python dependencies

- First, install the `uv` package manager for Python:
    * Linux/WSL: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    * MacOS: `brew install uv`
- Install python dependencies
    - Use `make install-dev` to install all dependencies including test dependencies
- Activate the virtual environment for your current terminal session via `source .venv/bin/activate`
- [optional] If you change something about the environment, you can lock your current env using `uv lock`

### Optional: Building the docker container using barebone

- From the root of the `barebone` repository use 
    - `uv run src/mki_barebone/main.py -i <relpath> -o <relpath>/tests/context/args --interface args` to re-built the container context with an `args` interface
    - `uv run src/mki_barebone/main.py -i <relpath> -o <relpath>/tests/context/grpc --interface grpc` to re-built the container context with a `grpc` interface
    - `relpath` is the relative path from the `barebone` repository to the root of this repository

### Building the docker container from context

- A pre-built docker image context can be found in `tests/context/<interface>`, where `<interface>` is either `args` or `grpc`
- Switch to the `tests/context/<interface>` directory and then use
    - `make docker` to build the tool container
    - The image name will be `scikit-metrics-tool`


## User instructions

- To run the tool first switch into `tests/workflow/cwl`
- Optional: Edit `job.json` to specify different function names and input files 
- Run `uv run cwltool workflow.cwl job.json` from console
- Result will be stored to `tests/workflow/cwl/result.json`

### Running tests

- Use `make test-unit` to run unit tests
- Use `make test-integration` to run integration tests that builds and brings up the whole workflow (cwl)
- Use `make test-barebone` to first create a context with the barebone and then run the integration test (cwl)
- Use `make test-all` to run all available tests (cwl and grpc tests)
- The latter two commands require the following project structure
    <root_dir>
    ├─ barebone // The barebone repo
    ├─ nodes
    |  ├─ scikit-metrics-tool // This repository
    ├─ orchestrator // For grpc tests
- Alternatively the paths in `tests/conftest.py` can be adjusted

## Coding rules for developers

- Please use PEP8-compliant syntax for your python scripts
    - You can use the Black Formater [VSCode Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
    - Reload window once after installing black to apply workspace settings
    - Use Shift + Alt + F to format your document automatically
    - Not required for the auto-generated grpc files ("*_pb2_grpc.py")
- Please use the `flake8` code linter for your python scripts
    - You can use this [VSCode Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8)
    - Reload window once after installing flake8 extension to apply workspace settings
    - Make sure VSCode does not show any errors before commiting code
    - Not required for the auto-generated grpc files ("*_pb2_grpc.py")
- Try to annotate your functions with a docstring
    - Use this [VSCode Extension](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) to autogenerate a docstring template
    - Example docstring:
    ```
        def compute_metric(self, request, context):
        """Dispatches the message to the exec function

        Args:
            request (RequestType): An "ExecutionMessage" (see tool.proto) containing information about the
              inputs and outputs for the tool
            context (): context information provided by grpc

        Returns:
            ResponseType: gRPC Message Wrapper of type "ExecutionMessage" (see tool.proto)
        """
        ...
    ```
    - We can autogenerate a HTML documentation from these docstrings using the `pdoc3` python package
        - Use `make -B docs` to autogenerate documentation
- Write tests for critical functions. Make sure all tests are passing before pushing
    - We use `pytest` for test execution
    - If you are working on a script in `src/mki-barebone/path/to/script.py` and want to write a function that tests a function called `func`, please include a test script `tests/path/to/test_script.py` and call the test function `test_func`
    - Execute required tests via `make test`
    - Execute all available tests via `make test-all` (may take a while)
