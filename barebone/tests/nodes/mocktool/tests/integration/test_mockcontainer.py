"""Tests for the mock container"""

import pytest
import re
import os
import json
import fsspec

from tests.integration.test_workflows import tool_workflow_cwl, tool_workflow_compose


def _mock_workflow_assertions_file(temp_dir) -> None:

    print(os.listdir(temp_dir))
    fs = fsspec.filesystem("file")
    # check that the correct output file has been generated
    result_file = os.path.join(temp_dir, "results", "result.json")

    assert fs.exists(result_file), f"{result_file} does not exist."
    with fs.open(result_file, "r") as fh:
        assert json.load(fh) == 42, "Function value returned must be 42"


def _mock_workflow_assertions(docker, tool_container, temp_dir) -> None:

    # check that result 42 was calculated
    assert re.search("Computed result 42 on input", docker.logs(tool_container)) is not None

    _mock_workflow_assertions_file(temp_dir)


def mock_workflow_cwl(mockcontainer_data):
    tool_workflow_cwl(*mockcontainer_data, _mock_workflow_assertions_file)


def mock_workflow_compose(mockcontainer_data, inputs=None):
    tool_workflow_compose(*mockcontainer_data, _mock_workflow_assertions, inputs=inputs)


@pytest.fixture
def workflow_data_compose(node_test_dir, node_context_dir, orch_context_dir, node_name, workflow_inputs):
    return (
        node_test_dir,
        node_context_dir,
        orch_context_dir,
        "workflow.yml",
        node_name,
        f"{node_name}-grpc",
    ), workflow_inputs


@pytest.mark.integration
@pytest.mark.mockcontainer
@pytest.mark.grpc
def test_mock_workflow_compose(workflow_data_compose) -> None:
    """
    Tests a mock workflow by bringing up a Docker Compose configuration,
    checking that all services are running and verifying the that the tool
    service is healthy and produced the expected output.
    """

    workflow_data, inputs = workflow_data_compose
    mock_workflow_compose(workflow_data, inputs)


@pytest.mark.integration
@pytest.mark.mockcontainer
@pytest.mark.cwl
def test_mock_workflow_cwl(node_workflow_dir) -> None:

    mock_workflow_cwl((node_workflow_dir,))
