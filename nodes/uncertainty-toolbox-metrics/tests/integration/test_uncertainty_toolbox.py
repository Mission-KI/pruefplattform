"""Tests for uncertainty-toolbox container"""

import pytest
import fsspec
from math import isclose
import os
from sys import float_info

from tests.integration.test_workflows import tool_workflow_compose, tool_workflow_cwl

from mki_barebone_io.arrow import load_arrow, parse_schema


def _assertions_container_workflow_file(temp_dir) -> None:

    expected_results = [0.08892045454545457, 0.0793308080808081]

    # check that the correct output file has been generated
    result_file = os.path.join(temp_dir, "results", "result.arrow")

    fs = fsspec.filesystem("file")
    assert fs.exists(result_file), f"{result_file} does not exist."

    metric_values = load_arrow(
        dict(location={"uri": result_file}),
        parse_schema([{"name": "metric_value", "type": "float64", "nullable": False}]),
    )

    assert len(metric_values) == len(expected_results)

    eps = float_info.epsilon
    for calc_value, test_value in zip(metric_values, expected_results):
        assert isclose(
            calc_value["metric_value"][0].as_py(), test_value, rel_tol=eps, abs_tol=eps
        )


def _assertions_container_workflow(docker, config, temp_dir):
    return _assertions_container_workflow_file(temp_dir)


def uncertainty_toolbox_workflow_compose(tool_container_data, inputs=None) -> None:
    """
    Tests a uncertainty-toolbox metric workflow by bringing up a Docker Compose
    configuration, checking that all services are running and verifying the that the tool
    service is healthy and produced the expected output.
    """

    tool_workflow_compose(
        *tool_container_data,
        test_func=_assertions_container_workflow,
        inputs=inputs,
    )


def uncertainty_toolbox_workflow_cwl(node_workflow_dir: str) -> None:
    """
    Tests a aif360 workflow by running a cwl configuration and verifying the that the workflow produced the expected output.
    """

    tool_workflow_cwl(
        *node_workflow_dir,
        test_func=_assertions_container_workflow_file,
    )


@pytest.fixture
def uct_compose_workflow_data(
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
@pytest.mark.uncertainty_toolbox
@pytest.mark.grpc
def test_uncertainty_toolbox_workflow_compose(uct_compose_workflow_data) -> None:
    """
    Tests a uncertainty toolbox workflow by bringing up a Docker Compose configuration,
    checking that all services are running and verifying the that the tool
    service is healthy and produced the expected output.
    """

    uct_container_data, inputs = uct_compose_workflow_data
    uncertainty_toolbox_workflow_compose(uct_container_data, inputs)


@pytest.mark.integration
@pytest.mark.uncertainty_toolbox
@pytest.mark.cwl
def test_uncertainty_toolbox_workflow_cwl(node_workflow_dir) -> None:
    """
    Tests a uncertainty toolbox workflow by running a cwl configuration and verifying the that the workflow produced the expected output.
    """

    uncertainty_toolbox_workflow_cwl((node_workflow_dir,))
