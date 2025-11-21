"""Tests for the scikit container created by the barebone"""

import pytest
import os

from test_barebone import call_create, check_filematch
from tests.integration.test_uncertainty_toolbox import uncertainty_toolbox_workflow_compose


@pytest.fixture(scope="module")
def call_create_grpc_docker_context_uct(
    barebone_dir, node_name, node_root_dir, generated_context_dir
):
    src = node_root_dir
    dest = os.path.join(generated_context_dir, "grpc")
    return call_create(barebone_dir, src, dest, interface="grpc")


@pytest.mark.barebone
@pytest.mark.uncertainty_toolbox
@pytest.mark.grpc
def test_create_uct_container_filematch(
    call_create_grpc_docker_context_uct, node_context_dir
):
    """Test a scikit image context created by the barebone via file matching

    Args:
        call_create_grpc_docker_context_uct: A pytest fixture that calls the barebone
        create_grpc_docker_context function
    """

    src, dest = call_create_grpc_docker_context_uct

    files_to_match = [
        "src/enpkg/grpc_backend/server.py",
        "src/enpkg/grpc_backend/utils.py",
        "src/enpkg/grpc_backend/module.proto",
        "src/enpkg/main.py",
        "src/enpkg/tool.py",
        "src/enpkg/uct_wrapper/impl.py",
        "pyproject.toml",
        "uv.lock",
        "spec.json",
        "Makefile",
    ]

    testsrc = os.path.join(node_context_dir, "grpc")

    check_filematch(dest, testsrc, files_to_match)


@pytest.mark.barebone
@pytest.mark.uncertainty_toolbox
@pytest.mark.grpc
def test_create_uct_docker(
    node_test_dir, node_context_dir, orch_context_dir, node_name, workflow_inputs
):
    """Test a scikit container created by the barebone via running a container workflow

    Args:
        call_create_scikit_container: A pytest fixture that calls the barebone create function
    """

    uncertainty_toolbox_workflow_compose(
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
