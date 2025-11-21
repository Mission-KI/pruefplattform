"""A mock orchestrator that sends execution messages to tools for testing purposes"""

import logging
from threading import Event
import argparse
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


DEFAULT_PIPELINE_SPEC = dict(
    tool_hostname="mock-tool",
    tool_port="8061",
    func="fourtytwo_wrapper",
    input=[
        dict(
            name="test_input",
            location=dict(uri=""),
        ),
    ],
    output=[dict(name="test_result", location=dict(uri="/results/result.json"))],
)


def orchestrate_grpc(pipeline_spec):
    """Execute a test orchestration with gRPC backends

    Args:
        pipeline_spec (dict): Specification of the tool to call (hostname, port, function, input files)
    """
    from grpc_backend.client import orchestrate

    logger.debug(f"{pipeline_spec}")
    orchestrate(pipeline_spec)


def main(tool_hostname: str, tool_port: int, tool_func: str, input_uri_list: list, output_uri_list: list):
    """Execute the orchestration

    Args:
        tool_hostname (str): Hostname of the tool container
        tool_port (int): Port the tool container listens to
        tool_func (str): Name of the function to call
        input_uri_list (list): List of uris that point to tool inputs
        output_uri_list (list): List of uris that point to tool outputs
    """

    pipeline_spec = dict(DEFAULT_PIPELINE_SPEC)
    pipeline_spec["tool_hostname"] = tool_hostname
    pipeline_spec["tool_port"] = tool_port
    pipeline_spec["func"] = tool_func

    for i in range(len(input_uri_list)):
        if len(pipeline_spec["input"]) <= i:
            pipeline_spec["input"].append(dict(name=f"input{i}", location=dict(uri=input_uri_list[i])))
        else:
            pipeline_spec["input"][i]["location"]["uri"] = input_uri_list[i]

    for i in range(len(output_uri_list)):
        if len(pipeline_spec["output"]) <= i:
            pipeline_spec["output"].append(dict(name=f"output{i}", location=dict(uri=output_uri_list[i])))
        else:
            pipeline_spec["output"][i]["location"]["uri"] = output_uri_list[i]

    orchestrate_grpc(pipeline_spec)

    # Wait forever
    Event().wait()


if __name__ == "__main__":

    logging.basicConfig()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tool_hostname", type=str, default=os.environ.get("TOOL_HOSTNAME", DEFAULT_PIPELINE_SPEC["tool_hostname"])
    )
    parser.add_argument(
        "--tool_port", type=int, default=os.environ.get("TOOL_PORT", DEFAULT_PIPELINE_SPEC["tool_port"])
    )
    parser.add_argument("--tool_func", type=str, default=os.environ.get("TOOL_FUNC", DEFAULT_PIPELINE_SPEC["func"]))
    parser.add_argument(
        "--input_uri_list",
        type=str,
        default=os.environ.get(
            "INPUT_URI_LIST", ",".join([input_spec["location"]["uri"] for input_spec in DEFAULT_PIPELINE_SPEC["input"]])
        ),
    )
    parser.add_argument(
        "--output_uri_list",
        type=str,
        default=os.environ.get(
            "OUTPUT_URI_LIST",
            ",".join([output_spec["location"]["uri"] for output_spec in DEFAULT_PIPELINE_SPEC["output"]]),
        ),
    )
    args = parser.parse_args()
    input_uri_list = args.input_uri_list.split(",")
    output_uri_list = args.output_uri_list.split(",")

    main(args.tool_hostname, args.tool_port, args.tool_func, input_uri_list, output_uri_list)
