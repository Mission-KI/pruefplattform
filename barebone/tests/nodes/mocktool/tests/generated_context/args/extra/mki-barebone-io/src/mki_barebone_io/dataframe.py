from urllib.parse import urlparse
import fsspec
import os

try:
    import pandas as pd
except ImportError:
    raise ImportError("Please install pandas to use pandas io features")


def _from_csv(uri: str, **fs_args) -> pd.DataFrame:

    parsed_uri = urlparse(uri)
    fs = fsspec.filesystem(parsed_uri.scheme, **fs_args)

    with fs.open(uri, "r") as f:
        return pd.read_csv(f)


def load_dataframe(artifact_node_msg: dict, **fs_args) -> pd.DataFrame:
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

    if ext == ".csv":
        return _from_csv(uri, **fs_args)

    raise NotImplementedError(f"Cannot load dataframe from a file with the {ext} file extension.")
