from pathlib import Path
import os

import pytest


NODE_NAME = "scikit-logreg-model"
NODE_ROOT_DIR = str(Path(__file__).resolve().parent.parent)
NODE_TEST_DIR = str(Path(__file__).resolve().parent)
NODE_CONTEXT_DIR = os.path.join(Path(__file__).resolve().parent, "context")
NODE_GENERATED_CONTEXT_DIR = os.path.join(NODE_TEST_DIR, "generated_context")
NODE_WORKFLOW_DIR = os.path.join(NODE_TEST_DIR, "workflow")

BAREBONE_DIR = os.path.join(
    Path(__file__).resolve().parent.parent.parent.parent, "barebone"
)

GRPC_ORCH_CONTEXT_DIR = os.path.join(
    Path(__file__).resolve().parent.parent.parent.parent, "orchestrator", "grpc_orch"
)


@pytest.fixture(scope="module")
def node_name():
    return NODE_NAME


@pytest.fixture(scope="module")
def node_root_dir():
    return NODE_ROOT_DIR


@pytest.fixture(scope="module")
def node_test_dir():
    return NODE_TEST_DIR


@pytest.fixture(scope="module")
def node_context_dir():
    return NODE_CONTEXT_DIR


@pytest.fixture(scope="module")
def barebone_dir():
    return BAREBONE_DIR


@pytest.fixture(scope="module")
def generated_context_dir():
    return NODE_GENERATED_CONTEXT_DIR


@pytest.fixture(scope="module")
def node_workflow_dir():
    return NODE_WORKFLOW_DIR


@pytest.fixture(scope="module")
def orch_context_dir():
    return GRPC_ORCH_CONTEXT_DIR


@pytest.fixture(scope="module")
def workflow_inputs(node_test_dir):
    test_data_dir = os.path.join(node_test_dir, "data")
    features_file = os.path.join(test_data_dir, "features.json")
    return [features_file]
