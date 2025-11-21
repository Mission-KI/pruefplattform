from urllib.parse import urlparse, urlunparse
import os
import json
import hashlib
import fsspec


def _from_json(uri: str, **fs_args) -> dict:

    parsed_uri = urlparse(uri)
    fs = fsspec.filesystem(parsed_uri.scheme, **fs_args)

    with fs.open(uri, "r") as f:
        return json.load(f)


def load_dict(artifact_node_msg: dict, **fs_args) -> dict:
    """Load a dictionary given an artifact node message
    Currently, dictionaries can be loaded from .json files

    Args:
        artifact_node_msg (dict): An artifact node message
        fs_args (dict): A dictionary of arguments to pass to the filesystem initializer

    Raises:
        NotImplementedError: If trying to load a resource / file format that is not supported

    Returns:
        dict: The ndarray described by the artifact node message
    """

    uri = artifact_node_msg["location"]["uri"]
    parsed_uri = urlparse(uri)

    file_path = parsed_uri.path
    _, ext = os.path.splitext(file_path)

    if ext == ".json":
        return _from_json(uri, **fs_args)

    raise NotImplementedError(f"Cannot load ndarray from a file with the {ext} file extension.")


def hash_dict(obj: dict):
    payload_digest = hashlib.sha256(json.dumps(obj).encode()).hexdigest()
    payload_id = f"sha256:{payload_digest}"
    return payload_id


def store_dict(obj: dict, artifact_node_msg: dict, hash_obj=True, **fs_args):
    """Store a dict as json file

    Args:
        obj (dict): The dict to store
        artifact_node_msg (dict): Output artifact node message
        fs_args (dict): A dictionary of arguments to pass to the filesystem initializer
    """

    if hash_obj:
        artifact_node_msg["payload_id"] = hash_dict(obj)

    uri = artifact_node_msg["location"]["uri"]
    parsed_uri = urlparse(uri)
    fs = fsspec.filesystem(parsed_uri.scheme, **fs_args)

    parent_path, filename = os.path.split(parsed_uri.path)
    parent_uri = urlunparse(
        (parsed_uri.scheme, parsed_uri.netloc, parent_path, parsed_uri.params, parsed_uri.query, parsed_uri.fragment)
    )
    if not fs.exists(parent_uri):
        fs.makedirs(parent_uri)

    with fs.open(uri, "w") as f:
        json.dump(obj, f)

    return artifact_node_msg
