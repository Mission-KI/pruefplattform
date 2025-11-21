"""Tests for the mock container"""

from pathlib import Path
import pytest
import fsspec
import re
import os
import json

from tests.integration.test_workflows import tool_workflow_compose, tool_workflow_cwl


def _assertions_aif360_workflow_file(temp_dir) -> None:

    fs = fsspec.filesystem("file")

    # check that the correct output file has been generated
    result_file = os.path.join(temp_dir, "results", "result.json")

    assert fs.exists(result_file), f"{result_file} does not exist."
    with fs.open(result_file, "r") as fh:
        assert (
            json.load(fh) == -0.12854990969960323
        ), "Function value returned must be -0.12854990969960323"


def _assertions_aif360_workflow(docker, tool_container, temp_dir) -> None:

    # check that result was calculated
    assert re.search("-0.12854990969960323", docker.logs(tool_container)) is not None

    _assertions_aif360_workflow_file(temp_dir)


def aif360_workflow_compose(aif_container_data, inputs=None) -> None:
    tool_workflow_compose(*aif_container_data, _assertions_aif360_workflow, inputs)


def aif360_workflow_cwl(aif_container_data) -> None:
    tool_workflow_cwl(*aif_container_data, _assertions_aif360_workflow_file)


@pytest.fixture(scope="module")
def aitf_compose_data(
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
@pytest.mark.aif360
@pytest.mark.grpc
def test_aif360_workflow_compose(aitf_compose_data) -> None:
    """
    Tests a aif360 workflow by bringing up a Docker Compose configuration,
    checking that all services are running and verifying the that the tool
    service is healthy and produced the expected output.
    """
    aitf_container_data, inputs = aitf_compose_data
    aif360_workflow_compose(aitf_container_data, inputs)


@pytest.mark.integration
@pytest.mark.aif360
@pytest.mark.cwl
def test_aif360_workflow_cwl(node_workflow_dir) -> None:
    """
    Tests a aif360 workflow by running a cwl configuration and verifying the that the workflow produced the expected output.
    """
    aif360_workflow_cwl((node_workflow_dir,))
