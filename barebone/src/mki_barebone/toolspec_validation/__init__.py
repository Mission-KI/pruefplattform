"""Validation utility to validate a given toolspec dictionary against the JSON schema for toolspecs"""

import json
import os
import jsonschema

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the toolspec_schema.json file
with open(os.path.join(current_dir, "toolspec_schema.json"), "r") as file:
    toolspec_schema = json.load(file)


def validate(toolspec):
    """
    Validates a given toolspec dictionary against the JSON schema for toolspecs.

    Args:
        toolspec (dict): The toolspec dictionary to be validated.

    Raises:
        Exception: If the toolspec does not conform to the schema,
        an exception is raised with details of the validation error.
    """
    try:
        jsonschema.validate(instance=toolspec, schema=toolspec_schema)
    except jsonschema.exceptions.ValidationError as err:
        raise Exception(f"toolspec.json is invalid: {err}")
