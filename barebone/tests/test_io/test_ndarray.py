from pathlib import Path
import pytest
import os


@pytest.fixture(scope="module")
def imports():
    from mki_barebone_io.ndarray import load_ndarray, store_ndarray
    import numpy as np

    return load_ndarray, store_ndarray, np


@pytest.fixture(scope="module")
def ndarray_fixture(imports):
    load_ndarray, store_ndarray, np = imports
    uri = os.path.join("tests", "test_io", "data", "true_labels.json")
    obj = load_ndarray(dict(location=dict(uri=uri)))
    return obj


@pytest.mark.unit
@pytest.mark.io
def test_load_ndarray(ndarray_fixture, imports):

    load_ndarray, store_ndarray, np = imports
    assert type(ndarray_fixture) is np.ndarray
    assert ndarray_fixture.shape == (40,)


@pytest.mark.unit
@pytest.mark.io
def test_store_ndarray(ndarray_fixture, imports):

    load_ndarray, store_ndarray, np = imports
    test_file = os.path.join("tests", "test_io", "data", "test.npy")
    store_ndarray(ndarray_fixture, dict(location=dict(uri=test_file)))
    assert os.path.exists(test_file)
    os.remove(test_file)
