import pytest
import os
from mki_barebone_io.dict import load_dict, store_dict


@pytest.fixture(scope="module")
def dict_fixture():
    obj = dict(this=dict(isa="test"), num=42)
    path = "data/d.json"
    artifact_node_msg = dict(location=dict(uri=path))
    store_dict(obj, artifact_node_msg)
    yield artifact_node_msg
    os.remove(path)


@pytest.mark.unit
@pytest.mark.io
def test_load_dict(dict_fixture):

    d = load_dict(dict_fixture)
    assert type(d) is dict
    assert type(d["this"]) is dict
    assert d["this"]["isa"] == "test"
    assert d["num"] == 42


@pytest.mark.unit
@pytest.mark.io
def test_store_dict(dict_fixture):
    assert os.path.exists(dict_fixture["location"]["uri"])
