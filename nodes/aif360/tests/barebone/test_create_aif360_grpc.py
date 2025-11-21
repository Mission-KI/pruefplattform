"""Tests for the scikit container created by the barebone"""

import pytest
import os

from test_barebone import call_create, check_filematch
from tests.integration.test_aif360 import aif360_workflow_compose


@pytest.fixture(scope="module")
def call_create_grpc_docker_context_aif360container(
    barebone_dir, node_name, node_root_dir, generated_context_dir
):
    src = node_root_dir
    dest = os.path.join(generated_context_dir, "grpc")
    return call_create(barebone_dir, src, dest, interface="grpc")


@pytest.mark.barebone
@pytest.mark.aif360
@pytest.mark.grpc
def test_create_aif360_container_filematch(
    call_create_grpc_docker_context_aif360container, node_context_dir
):
    """Test a scikit image context created by the barebone via file matching

    Args:
        call_create_grpc_docker_context_aif360container: A pytest fixture that calls the barebone
        create function
        node_context_dir: A pytest fixture pointing to the node context directory
    """

    src, dest = call_create_grpc_docker_context_aif360container

    files_to_match = [
        "src/enpkg/grpc_backend/server.py",
        "src/enpkg/grpc_backend/utils.py",
        "src/enpkg/grpc_backend/module.proto",
        "src/enpkg/main.py",
        "src/enpkg/tool.py",
        "src/enpkg/aif360_wrapper/wrapper.py",
        "pyproject.toml",
        "uv.lock",
        "spec.json",
        "Makefile",
    ]

    testsrc = os.path.join(node_context_dir, "grpc")

    check_filematch(dest, testsrc, files_to_match)


@pytest.mark.barebone
@pytest.mark.aif360
@pytest.mark.grpc
def test_create_aif360_docker(
    node_test_dir, node_context_dir, orch_context_dir, node_name, workflow_inputs
):
    """Test a aif360 container created by the barebone via running a container workflow

    Args:
        call_create_aif360_container: A pytest fixture that calls the barebone create function
        node_test_dir (str): A pytest fixture that is the path to the nodes tests directory
        node_context_dir (str): A pytest fixture that is the path to the nodes context directory
        orch_context_dir (str): A pytest fixture that is the path to the grpc orchestrator context
        node_name (str): A pytest fixture that is the path to the nodes name
        workflow_inputs (list): A pytest fixture with paths to the workflow inputs
    """

    aif360_workflow_compose(
        (
            node_test_dir,
            node_context_dir,
            orch_context_dir,
            "workflow.yml",
            node_name,
            f"{node_name}-grpc",
        ),
        workflow_inputs,
    )
