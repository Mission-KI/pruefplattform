"""Tests for the scikit container created by the barebone"""

import pytest
import os
from test_barebone import call_create, check_filematch
from tests.integration.test_aif360 import aif360_workflow_cwl


@pytest.fixture(scope="module")
def call_create_args_docker_context_aif360container(
    barebone_dir, node_name, node_root_dir, generated_context_dir
):
    src = node_root_dir
    dest = os.path.join(generated_context_dir, "args")
    return call_create(barebone_dir, src, dest, interface="args")


@pytest.mark.barebone
@pytest.mark.aif360
@pytest.mark.cwl
def test_create_aif360_container_filematch(
    call_create_args_docker_context_aif360container, node_context_dir
):
    """Test a aif360 image context created by the barebone via file matching

    Args:
        call_create_args_docker_context_aif360container: A pytest fixture that calls the barebone function
    """

    src, dest = call_create_args_docker_context_aif360container

    files_to_match = [
        "src/enpkg/args_backend/argexec.py",
        "src/enpkg/main.py",
        "src/enpkg/tool.py",
        "src/enpkg/aif360_wrapper/wrapper.py",
        "pyproject.toml",
        "uv.lock",
        "spec.json",
        "Makefile",
    ]

    testsrc = os.path.join(node_context_dir, "args")

    check_filematch(dest, testsrc, files_to_match)


@pytest.mark.barebone
@pytest.mark.aif360
@pytest.mark.cwl
def test_create_aif360_docker(
    call_create_args_docker_context_aif360container, node_workflow_dir
):
    """Test a aif360 container created by the barebone via running a container workflow

    Args:
        call_create_aif360_container: A pytest fixture that calls the barebone create function
        node_workflow_dir (str): A pytest fixture that is the directory to the cwl workflow files
    """

    src, dest = call_create_args_docker_context_aif360container
    aif360_workflow_cwl((node_workflow_dir,))
