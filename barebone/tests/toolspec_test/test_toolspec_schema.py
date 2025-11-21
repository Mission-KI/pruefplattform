import json
from mki_barebone.toolspec_validation import validate
import os
import pytest

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


@pytest.mark.barebone
@pytest.mark.unit
def test_spec_json_general_reference_correct():
    expect_spec_correct("spec_ref1.json")
    expect_spec_correct("spec_ref2.json")


@pytest.mark.barebone
@pytest.mark.unit
def test_spec_mocktool_correct():
    expect_spec_correct("../nodes/mocktool/spec.json")


@pytest.mark.barebone
@pytest.mark.unit
def test_spec_json_syntax_error():
    with pytest.raises(json.JSONDecodeError):
        load_json(os.path.join(current_dir, "spec_syntax_error.json"))


@pytest.mark.barebone
@pytest.mark.unit
def test_spec_json_wrong_property():
    spec = load_json(os.path.join(current_dir, "spec_wrong_property.json"))
    with pytest.raises(Exception):
        validate(spec)


def expect_spec_correct(rel_path_of_spec):
    spec = load_json(os.path.join(current_dir, rel_path_of_spec))
    try:
        validate(spec)
    except Exception as err:
        pytest.fail(f"spec.json of {rel_path_of_spec} is invalid: {err}")


if __name__ == "__main__":
    pytest.main()
