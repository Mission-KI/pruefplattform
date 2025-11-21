"""Main entrypoint for a container serving a gRPC backend to exchange execution messages"""

import logging

import argparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def serve_grpc(port: int):
    """Start a gRPC server for exchanging execution messages

    Args:
        port (int): Port to serve to

    Returns:
        grpc.server: The running gRPC server instance
    """
    from grpc_backend.server import serve

    return serve(port=port)


def grpc_main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8061, help="The port of the gRPC server (if gRPC is being used)")
    args = parser.parse_args()
    serve_grpc(args.port).wait_for_termination()


def args_main():

    from args_backend.argexec import exec
    exec()


if __name__ == "__main__":

    logging.basicConfig()
    
    args_main()