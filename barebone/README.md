# mki-barebone

A tool for building containers that are compatible with the MISSION KI platform.

## Project structure

- docs: auto generated html docs from docstrings (experimental)
- tests: Test scripts for the barebone (pytest + reference mock server/orchestrator implementations)
- .gitignore: Files not to commit/push
- .gitlab-ci.yml: Configuration for the CI runner (experimental)
- src: Source code containing the package "mki-barebone" which contains the entrypoint script for the barebone "main.py"
- Makefile: Build file for the docs and barebone
- README.md: this readme 
- pyproject.toml: python package specification including requirements
- uv.lock: A lockfile created by `uv` for better reproducibility of the python environment and dependencies

## Installation

### Linux shell on windows with wsl

- We are developing mostly in a linux environment / with linux tool, it is recommended to install WSL2 under windows
- In powershell use ``wsl -d <DISTRO>``, e.g. ``wsl -d Ubuntu``, to access a linux shell under windows
- Use can use `git`, `docker`, `make` etc. as expected in the linux shell
- Also you can activate python virtual environments using `source <name>/bin/activate`

### Installation

- First, install the `uv` package manager for Python:
    * Linux/WSL: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    * MacOS: `brew install uv`
- Install python dependencies
    - Use `make install` for a minimal install (recommended for standard users)
    - Use `make install-dev` to install all dependencies including test dependencies (recommended for developers)
- Activate the virtual environment for your current terminal session via `source .venv/bin/activate`
- [optional] If you change something about the environment, you can lock your current env using `uv lock`

## User instructions

- You can either initialize a new project for tool development or adapt existing python projects
    - Using the barebone requires the python source files to be stored in a directory following common python packaging guidelines. At the very least you need
        - a `src` directory, containining a package directory `src/enpkg` 
        - a script of wrapper functions inside a subpackage directory `src/enpkg/<pkg>/<wrapper>.py`, for example `src/enpkg/toolpkg/wrapper.py`
        - Wrapper functions must have the interface `def <func>(execution_msg: dict) -> dict`, retrieving and returning an execution message object
        - An execution message object is a python dict with the following content `dict(func=<func>, inputs=<input_list>, outputs=<output_list>)`, where
            - `func` is a `string` describing the function name
            - `input_list` is a list of dict with signature `dict(location=<location>)` and `location` is a dict with signature `dict(uri=<uri>)` and `uri` is a string resprenting a path or uri to an input
            - `output_list` is a list of dict with signature `dict(location=<location>)` and `location` is a dict with signature `dict(uri=<uri>)` and `uri` is a string resprenting a path or uri to an ouput
        - a `pyproject.toml` specifying python package dependencies of the tool. Using the `grpc` interface requires adding the dependencies `"fsspec>=2025.3.0", "grpcio-tools>=1.71.0"` 
        - a `spec.json` that is the tool specification (more details can be found in the deliverable document)
    - To initialize a new project for tool development use `./init.sh` and follow the instructions
        - This creates a new directory with the required folder structure and further instructions
    - At any point, but at least once before using the barebone build tool, pin your dependencies in a lockfile via `uv sync` and `uv lock`
        - There should be a `uv.lock` file in the directory

- Given a directory with tool source files that meets the requirements, you can build a container via
    - `uv run src/mki_barebone/main.py -i <input_dir> -o <output_dir> --interface <interface>`
    - `<input_dir>` is the path to the directory with the tool source files
    - `<output_dir>` is the path to a directory in which the container context will be created
    - `<interface>` can be either `args` to create a container with command-line interface or `grpc` for grpc interface (experimental). The default `args` is recommended

### Running tests

- Use `make test-unit` to run unit tests
- Use `make test-integration` to run integration tests that builds and brings up the whole workflow (cwl)
- Use `make test-barebone` to first create a context with the barebone and then run the integration test (cwl)
- Use `make test-all` to run all available tests (cwl and grpc tests)
- The latter two commands require the following project structure
    <root_dir>
    ├─ barebone // This repo
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
