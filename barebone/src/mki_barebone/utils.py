"""Utility functions used by the main script for uri and path normalization"""

from urllib.parse import urlparse, urlunparse
import os


class CwdContextManager:
    """A context manager for more safer use of subprocess(.., cwd=..)
    Ensures the original cwd is recovered
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.cwd = None

    def __enter__(self):
        self.cwd = os.path.realpath(os.getcwd())

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            cur_cwd = os.path.realpath(os.getcwd())
            if cur_cwd != self.cwd:
                os.chdir(self.cwd)
                if self.logger is not None:
                    self.logger.debug(f"Switched cwd back to {self.cwd}")
        except Exception:
            os.chdir(self.cwd)
            if self.logger is not None:
                self.logger.debug(f"Switched cwd back to {self.cwd}")


def normalize_uri(uri: str) -> str:
    """Normalizes a uri

    Args:
        uri (str): unnormalized uri

    Returns:
        str: normalized uri
    """
    parsed_uri = urlparse(uri)
    path = normalize_path(parsed_uri.path)
    return urlunparse(
        (parsed_uri.scheme, parsed_uri.netloc, path, parsed_uri.query, parsed_uri.params, parsed_uri.fragment)
    )


def normalize_path(path: str) -> str:
    """Normalizes a filesystem path

    Args:
        path (str): Unnormalized path

    Returns:
        str: normalized path
    """
    if path.endswith("/"):
        return path
    else:
        return path + "/"
