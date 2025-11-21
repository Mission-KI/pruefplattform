"""Utility functions for converting execution messages from grpc messages to dict and vice versa"""

import grpc_backend.module_pb2 as module_pb2


def artifact_node_message_from_dict(d):
    """Creates an ArtifactNodeMessage from a python dict

    Args:
        d (dict): Python dict containing keywords like an ArtifactNodeMessage

    Returns:
        ResponseType: gRPC message wrapper for a ArtifactNodeMessage
    """
    return module_pb2.ArtifactNodeMessage(
        name=d.get("name"),
        location=module_pb2.ArtifactNodeLocation(uri=d.get("location", {}).get("uri")),
        payload_id=d.get("payload_id"),
    )


def artifact_node_message_to_dict(msg):
    """Converts an ArtifactNodeMessage to a python dict

    Args:
        msg (RequestType): gRPC message wrapper of an ArtifactNodeMessage

    Returns:
        dict: The ArtifactNodeMessage as a python dict
    """
    return dict(
        name=msg.name,
        location=dict(
            uri=msg.location.uri,
        ),
        payload_id=msg.payload_id,
    )


def execution_message_from_dict(d):
    """Creates an ExecutionMessage from a python dict

    Args:
        d (dict): Python dict containing keywords like an ExecutionMessage

    Returns:
        ResponseType: gRPC message wrapper for a ExecutionMessage
    """

    return module_pb2.ExecutionMessage(
        func=d.get("func"),
        input=[artifact_node_message_from_dict(inp) for inp in d.get("input", [])],
        output=[artifact_node_message_from_dict(inp) for inp in d.get("output", [])],
        meta=module_pb2.ExecutionMeta(execution_name=d.get("meta", {}).get("execution_name")),
    )


def execution_message_to_dict(msg):
    """Converts an ExecutionMessage to a python dict

    Args:
        msg (RequestType): gRPC message wrapper of an ExecutionMessage

    Returns:
        dict: The ExecutionMessage as a python dict
    """

    return dict(
        func=msg.func,
        input=[artifact_node_message_to_dict(node_msg) for node_msg in msg.input],
        output=[artifact_node_message_to_dict(node_msg) for node_msg in msg.output],
        meta=dict(execution_name=msg.meta.execution_name),
    )