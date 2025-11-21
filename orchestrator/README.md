# Orchestrator

An orchestrator for running MissionKI platform workflows

## Project structure

    orchestrator/
    ├─ cwl_orch/
    │  ├─ Makefile // For installing cwltool using `make install` and running the test workflows
    ├─ grpc_orch // An experimental gRPC orchestrator for executing simple workflows with containers using the gRPC interface
    ├─ tests/
    │  ├─ nodes/
    │  │  ├─ mocktool // docker context for mocktool
    |  │  │  ├─ tests
    |  |  │  │  ├─ context
    │  │  ├─ mockmodel // docker context for mockmodel
    │  ├─ workflows/
    │  │  ├─ mockworkflow // mock workflow with model and tool/
    │  │  │  ├─ workflow.cwl // cwl example
    │  │  │  ├─ job.json
    │  │  ├─ scikit-workflow // scikit workflow with model and tool, requires scikit-metrics-tool and scikit-logreg-model in parent directories
    │  │  │  ├─ cwl   
    |  |  |  |  ├─ workflow.cwl // cwl example
    │  │  │  |  ├─ job.json
    ├─ README.md // this file
    ├─ .gitignore

## Installation

### Linux shell on windows with wsl

- We are developing mostly in a linux environment / with linux tool, it is recommended to install WSL2 under windows
- In powershell use ``wsl -d <DISTRO>``, e.g. ``wsl -d Ubuntu``, to access a linux shell under windows
- Use can use `git`, `docker`, `make` etc. as expected in the linux shell
- Also you can activate python virtual environments using `source <name>/bin/activate`

### Installation of uv

- First, install the `uv` package manager for Python:
    * Linux/WSL: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    * MacOS: `brew install uv`

## User instructions

### Running predefined workflow (cwl)

- To run a mock workflow with a model node and a tool node 
    - switch to `cwl_orch` directory
    - run `make run-mock-workflow`

- To run a scikit workflow with a model node and a tool node 
    - Make sure the following folder structure is in place
    <root_dir>
    ├─ orchestrator
    ├─ nodes
    │  ├─ scikit-metrics-tool // the predefined scikit-metrics tool
    │  ├─ scikit-logreg-model // the predefined scikit logreg model
    - Optional: switch to `tests/workflows/scikit-workflow/cwl` directory and edit the `job.json` to execute different functions and use different input files
    - switch to `cwl_orch` directory
    - run `make run-scikit-workflow`

## Python Coding rules for developers

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

- Write tests for critical functions. Make sure all tests are passing before pushing

