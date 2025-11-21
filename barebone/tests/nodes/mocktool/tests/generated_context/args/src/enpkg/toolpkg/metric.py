import logging
import json
import hashlib
import fsspec
import os
from urllib.parse import urlparse

from mki_barebone_io.dict import store_dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def fourtyone():
    return 41


def fourtytwo():
    return 42


def barebone_wrapper(func, execution_msg):
    """Function that wraps tool functionality

    Args:
        execution_msg (dict): An ExecutionMessage containing information about the inputs for and wanted outputs
        of the tool function

    Returns:
        dict: An ExecutionMessage containing information about the inputs and outputs of the tool function
    """

    # get uri info from execution message
    input_artifact = execution_msg["input"][0]
    output_artifact = execution_msg["output"][0]

    # do any computations
    result = func()
    logger.debug(f"Computed result {result} on input {input_artifact['location']['uri']}")

    # store results, the format needs to be specified in the execution node manifest model.json
    output_artifact = store_dict(result, output_artifact)

    # return dict execution message
    return dict(
        func=execution_msg["func"],
        input=execution_msg["input"],
        output=[output_artifact],
        meta=execution_msg["meta"],
    )


def fourtytwo_wrapper(execution_msg: dict) -> dict:
    """Function that wraps a function returning fourtytwo

    Args:
        execution_msg (dict): An ExecutionMessage containing information about the inputs for and wanted outputs
        of the tool function

    Returns:
        dict: An ExecutionMessage containing information about the inputs and outputs of the tool function
    """

    return barebone_wrapper(fourtytwo, execution_msg)


def fourtyone_wrapper(execution_msg: dict) -> dict:
    """Function that wraps a function returning fourtytwo

    Args:
        execution_msg (dict): An ExecutionMessage containing information about the inputs for and wanted outputs
        of the tool function

    Returns:
        dict: An ExecutionMessage containing information about the inputs and outputs of the tool function
    """

    return barebone_wrapper(fourtyone, execution_msg)
