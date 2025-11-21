"""gRPC Server for dispatching execution messages to underlying python tool functions"""

import grpc
import concurrent.futures as futures

import grpc_backend.module_pb2_grpc as module_pb2_grpc

from grpc_backend.utils import execution_message_from_dict, execution_message_to_dict
from tool import funcwrapper

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ModuleServicer(module_pb2_grpc.ModuleServicer):
    """A gRPC Servicer that provides a service for dispatching execution messages to tool function wrappers"""

    def exec(self, request, context):
        """Dispatches the message to the exec function

        Args:
            request (Python gRPC-Message): An "ExecutionMessage" (see tool.proto) containing information about the
              inputs and outputs for the tool
            context (): context information provided by grpc

        Returns:
            gRPC Python Message: of type "ExecutionMessage" (see tool.proto)
        """

        logger.debug(f"Executing function {request.func}")
        exec_message = execution_message_to_dict(request)
        exec_response = funcwrapper(exec_message)
        logger.debug(exec_response)
        return execution_message_from_dict(exec_response)


def serve(port=8061):
    """Factory to create a grpc server that provides the module service

    Args:
        port (int, optional): Port to listen to. Defaults to 8061.

    Returns:
        grpc.server: The gRPC server object
    """

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    module_pb2_grpc.add_ModuleServicer_to_server(ModuleServicer(), server)

    server.add_insecure_port("[::]:{}".format(port))
    logger.debug(f"Start server to port {port}")
    server.start()

    return server