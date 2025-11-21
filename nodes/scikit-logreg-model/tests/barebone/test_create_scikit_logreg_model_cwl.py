"""Tests for the scikit container created by the barebone"""

import pytest
import os
from test_barebone import call_create, check_filematch
from tests.integration.test_scikit_logreg_model import scikit_logreg_model_workflow_cwl


@pytest.fixture(scope="module")
def call_create_args_docker_context_scikit_logreg_model(
    barebone_dir, node_name, node_root_dir, generated_context_dir
):
    src = node_root_dir
    dest = os.path.join(generated_context_dir, "args")
    return call_create(barebone_dir, src, dest, interface="args")


@pytest.mark.barebone
@pytest.mark.scikit_logreg_model
def test_create_args_docker_context_scikit_logreg_model(
    call_create_args_docker_context_scikit_logreg_model, node_context_dir
):
    """Test a scikit_logreg_model image context created by the barebone via file matching

    Args:
        call_create_args_docker_context_scikit_logreg_model: A pytest fixture that calls the barebone function
    """

    src, dest = call_create_args_docker_context_scikit_logreg_model

    files_to_match = [
        "src/enpkg/args_backend/argexec.py",
        "src/enpkg/main.py",
        "src/enpkg/tool.py",
        "src/enpkg/logreg_model_wrapper/impl.py",
        "pyproject.toml",
        "uv.lock",
        "spec.json",
        "Makefile",
    ]

    testsrc = os.path.join(node_context_dir, "args")

    check_filematch(dest, testsrc, files_to_match)


@pytest.mark.barebone
@pytest.mark.scikit_logreg_model
def test_create_scikit_logreg_model_container_docker(
    call_create_args_docker_context_scikit_logreg_model, node_workflow_dir
):
    """Test a scikit_logreg_model container created by the barebone via running a container workflow

    Args:
        call_create_args_docker_context_scikit_logreg_model: A pytest fixture that calls the barebone create function
    """

    src, dest = call_create_args_docker_context_scikit_logreg_model
    scikit_logreg_model_workflow_cwl((node_workflow_dir,))
