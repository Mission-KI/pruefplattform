from urllib.parse import urlparse, urlunparse
import os
import json
import fsspec

try:
    import numpy as np
except ImportError:
    raise ImportError("Please install numpy to use numpy io features")


def _from_npy(uri: str, **fs_args) -> np.ndarray:

    parsed_uri = urlparse(uri)
    fs = fsspec.filesystem(parsed_uri.scheme, **fs_args)

    with fs.open(uri) as f:
        arr = np.load(f)
    return arr


def _from_json(uri: str, **fs_args) -> np.ndarray:

    parsed_uri = urlparse(uri)
    fs = fsspec.filesystem(parsed_uri.scheme, **fs_args)

    with fs.open(uri, "r") as f:
        return np.array(json.load(f))


def load_ndarray(artifact_node_msg: dict, **fs_args) -> np.ndarray:
    """Load an ndarray given an artifact node message
    Currently, ndarrays can be loaded from .npy or .json files

    Args:
        artifact_node_msg (dict): An artifact node message
        fs_args (dict): A dictionary of arguments to pass to the filesystem initializer

    Raises:
        NotImplementedError: If trying to load a resource / file format that is not supported

    Returns:
        np.ndarray: The ndarray described by the artifact node message
    """

    uri = artifact_node_msg["location"]["uri"]
    parsed_uri = urlparse(uri)

    file_path = parsed_uri.path
    _, ext = os.path.splitext(file_path)

    if ext == ".json":
        return _from_json(uri, **fs_args)

    if ext == ".npy":
        return _from_npy(uri, **fs_args)

    raise NotImplementedError(f"Cannot load ndarray from a file with the {ext} file extension.")


def hash_ndarray():
    pass


def store_ndarray(obj: np.ndarray, artifact_node_message: dict, hash_obj=True, **fs_args):
    """Store an numpy ndarray to uri

    Args:
        obj (np.ndarray): The numpy array to store
        artifact_node_message (dict): Output artifact node message
        fs_args (dict): A dictionary of arguments to pass to the filesystem initializer
    """

    uri = artifact_node_message["location"]["uri"]
    parsed_uri = urlparse(uri)
    fs = fsspec.filesystem(parsed_uri.scheme, **fs_args)

    parent_path, filename = os.path.split(parsed_uri.path)
    parent_uri = urlunparse(
        (parsed_uri.scheme, parsed_uri.netloc, parent_path, parsed_uri.params, parsed_uri.query, parsed_uri.fragment)
    )
    if not fs.exists(parent_uri):
        fs.makedirs(parent_uri)

    with fs.open(uri, "wb") as f:
        np.save(f, obj)

    return artifact_node_message
