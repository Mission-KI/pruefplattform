"""gRPC client for tool orchestration"""

import grpc
import grpc_backend.module_pb2_grpc as module_pb2_grpc

from grpc_backend.utils import execution_message_from_dict

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def orchestrate(pipeline_spec):
    """Executes a simple orchestration given the pipeline_spec
    Currently, only a simple pipeline with a single tool is supported.

    Args:
        pipeline_spec (dict): Specification of the pipeline to execute.
        Needs to contain the fields tool_hostname, tool_port, input and output
    """
    with grpc.insecure_channel(f"{pipeline_spec['tool_hostname']}:{pipeline_spec['tool_port']}") as channel:

        stub = module_pb2_grpc.ModuleStub(channel)

        exec_msg_dict = dict(
            func=pipeline_spec["func"], input=pipeline_spec["input"], output=pipeline_spec["output"]
        )
        exec_msg = execution_message_from_dict(exec_msg_dict)

        logger.info(f"Calling the tool with message {exec_msg_dict}")
        response = stub.exec(exec_msg)
        logger.info(response)
