"""Tests for the mock container"""

import pytest
import fsspec
import re
import os
import json

from tests.integration.test_workflows import tool_workflow_compose, tool_workflow_cwl


def _assertions_scikit_workflow_file(temp_dir) -> None:

    fs = fsspec.filesystem("file")

    # check that the correct output file has been generated
    result_file = os.path.join(temp_dir, "results", "result.json")

    assert fs.exists(result_file), f"{result_file} does not exist."
    with fs.open(result_file, "r") as fh:
        assert (
            json.load(fh)["accuracy"] == 0.875
        ), "Function value returned must be 0.875"


def _assertions_scikit_workflow(docker, tool_container, temp_dir) -> None:

    # check that result 42 was calculated
    assert (
        re.search("Computed accuracy: 0.875", docker.logs(tool_container)) is not None
    )
    _assertions_scikit_workflow_file(temp_dir)


def scikit_workflow_compose(scikit_container_data, inputs=None) -> None:
    tool_workflow_compose(
        *scikit_container_data, _assertions_scikit_workflow, inputs=inputs
    )


def scikit_workflow_cwl(scikit_container_data) -> None:
    tool_workflow_cwl(*scikit_container_data, _assertions_scikit_workflow_file)


@pytest.fixture
def scikit_compose_workflow_data(
    node_test_dir, node_context_dir, orch_context_dir, node_name, workflow_inputs
):
    return (
        node_test_dir,
        node_context_dir,
        orch_context_dir,
        "workflow.yml",
        node_name,
        f"{node_name}-grpc",
    ), workflow_inputs


@pytest.mark.integration
@pytest.mark.scikit
@pytest.mark.grpc
def test_scikit_workflow_compose(scikit_compose_workflow_data) -> None:
    """
    Tests a scikit workflow by bringing up a Docker Compose configuration,
    checking that all services are running and verifying the that the tool
    service is healthy and produced the expected output.
    """

    scikit_container_data, inputs = scikit_compose_workflow_data
    scikit_workflow_compose(scikit_container_data, inputs)


@pytest.mark.integration
@pytest.mark.scikit
@pytest.mark.cwl
def test_scikit_workflow_cwl(node_workflow_dir) -> None:
    """
    Tests a scikit workflow by running a cwl configuration and verifying the that the workflow produced the expected output.
    """

    scikit_workflow_cwl((node_workflow_dir,))
