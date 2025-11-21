"""Tests for the mock container"""

import pytest
import fsspec
import re
import os
import json

from tests.integration.test_workflows import tool_workflow_cwl, tool_workflow_compose


def _assertions_scikit_logreg_model_workflow_file(temp_dir) -> None:

    fs = fsspec.filesystem("file")

    # fmt: off
    expected_result = [
        0, 1, 0, 0, 1, 1, 0, 0, 1, 1,
        1, 1, 0, 1, 0, 0, 0, 1, 1, 0,
        0, 0, 1, 1, 1, 1, 1, 0, 0, 0,
        1, 1, 1, 1, 0, 1, 1, 0, 1, 1,
    ]
    # fmt: on

    # check that the correct output file has been generated
    result_file = os.path.join(temp_dir, "results", "result.json")

    assert fs.exists(result_file), f"{result_file} does not exist."
    with fs.open(result_file, "r") as fh:
        assert (
            json.load(fh) == expected_result
        ), f"Function value returned must be {expected_result}"


def _assertions_scikit_logreg_model_workflow(docker, tool_container, temp_dir) -> None:

    # fmt: off
    expected_result = [
        0, 1, 0, 0, 1, 1, 0, 0, 1, 1,
        1, 1, 0, 1, 0, 0, 0, 1, 1, 0,
        0, 0, 1, 1, 1, 1, 1, 0, 0, 0,
        1, 1, 1, 1, 0, 1, 1, 0, 1, 1,
    ]
    # fmt: on

    # check that the correct result calculated
    assert re.search(f"{expected_result}", docker.logs(tool_container)) is not None

    _assertions_scikit_logreg_model_workflow_file(temp_dir)


def scikit_logreg_model_workflow_compose(container_data, inputs=None) -> None:
    tool_workflow_compose(
        *container_data, _assertions_scikit_logreg_model_workflow, inputs=inputs
    )


def scikit_logreg_model_workflow_cwl(container_data) -> None:
    tool_workflow_cwl(*container_data, _assertions_scikit_logreg_model_workflow_file)


@pytest.fixture
def workflow_data_compose(
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
@pytest.mark.scikit_logreg_model
@pytest.mark.grpc
def test_scikit_logreg_model_workflow_compose(workflow_data_compose) -> None:
    """
    Tests a scikit model prediction workflow by bringing up a Docker Compose
    configuration, checking that all services are running and verifying the that the tool
    service is healthy and produced the expected output.
    """

    container_data, inputs = workflow_data_compose
    scikit_logreg_model_workflow_compose(container_data, inputs)


@pytest.mark.integration
@pytest.mark.scikit_logreg_model
@pytest.mark.grpc
def test_scikit_logreg_model_workflow_cwl(node_workflow_dir) -> None:

    scikit_logreg_model_workflow_cwl((node_workflow_dir,))
