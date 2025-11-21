from urllib.parse import urlparse
import os
from mki_barebone_io.registry import EXT_TO_LOADER


def load(execution_msg: dict):
    """Try to load all input resources described in the execution message
    The in-memory object to load will be inferred from the uri
    Currently only .npy-files are supported, which will load into numpy.ndarray objects

    Args:
        execution_msg (dict): _description_

    Raises:
        NotImplementedError: If the execution message contains a reference to a resource with no available loader

    Returns:
        list : List of python objects corresponding to the artifact nodes specified in the execution message
    """

    artifact_node_obj = []
    for artifact_node_msg in execution_msg["input"]:
        uri = artifact_node_msg["location"]["uri"]
        parsed_uri = urlparse(uri)

        # Infer from uri
        if parsed_uri.scheme in ["", "file"]:
            _, ext = os.path.splitext(parsed_uri.path)

            if ext not in EXT_TO_LOADER:
                raise NotImplementedError(f"There is no loader available matching to {ext}")
            obj = EXT_TO_LOADER[ext](artifact_node_msg)
            artifact_node_obj.append(obj)
    return artifact_node_obj
