"""Python module for building tool containers compatible with the MISSION KI platform concept

Typical usage example:
python main.py -i <input_dir> -o <output_dir>
"""

import argparse
from urllib.parse import urlparse, urljoin
import fsspec
import jsonref
import subprocess
import logging
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from mki_barebone.toolspec_validation import validate
from mki_barebone.utils import normalize_uri, normalize_path, CwdContextManager

from python_on_whales import docker

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SPEC_FILENAME = "spec.json"
PYPROJECT_FILENAME = "pyproject.toml"
UVLOCK_FILENAME = "uv.lock"
PYTHONVERSION_FILENAME = ".python-version"
TEMPLATES_DIRECTORY = "src/mki_barebone/templates"
GRPC_TEMPLATES = [
    "src/enpkg/grpc_backend/server.py",
    "src/enpkg/grpc_backend/utils.py",
    "src/enpkg/grpc_backend/module.proto",
    "src/enpkg/main.py.jinja",
    "src/enpkg/tool.py.jinja",
    "Dockerfile.jinja",
    "Makefile.jinja",  # optional
    ".dockerignore",  # optional
]

ARGS_TEMPLATES = [
    "src/enpkg/args_backend/argexec.py",
    "src/enpkg/main.py.jinja",
    "src/enpkg/tool.py.jinja",
    "Dockerfile.jinja",
    "Makefile.jinja",  # optional
    ".dockerignore",  # optional
    "tool.cwl.jinja"
]


def _parse_spec(src, interface="args"):
    """Reads and validates the tool spec

    Args:
        src (str): uri pointing to the source folder

    Raises:
        FileNotFoundError: If spec or files specified in the spec are not found
        ValueError: Invalid format

    Returns:
        dict: Flat dictionary for template rendering
        dict: Flat dictionary of fully qualified uris
    """

    # Init filesystem
    parsed_uri = urlparse(src)
    fs = fsspec.filesystem(parsed_uri.scheme)

    # Read spec
    specuri = urljoin(src, SPEC_FILENAME)
    with fs.open(specuri, "r", encoding="utf8") as f:
        spec = jsonref.loads(f.read())

    # Validate json
    # TODO: Create json schema, validate here

    name = spec["id"]["name"]
    if interface == "grpc":
        name += "-grpc"
    servicename = name[0].upper() + name[1:]

    functions = []
    packages = dict()
    for function in spec["functions"].values():

        pkg = function["package"]
        pkgname = pkg["name"]
        pkgpath = pkg["path"]
        pkguri = urljoin(src, normalize_path(pkgpath))
        if not fs.exists(pkguri):
            raise FileNotFoundError(f"Python package {pkgname} does not exist at {pkguri}.")
        if pkgname not in packages:
            packages[pkgname] = dict(path=pkgpath, uri=pkguri)

        scriptfile = function["script"]
        scriptname, scriptext = os.path.splitext(str(scriptfile))
        if scriptext != ".py":
            raise NotImplementedError(
                "Specified script must be a python file (.py extension)," + f"but has extension {scriptext}"
            )
        scripturi = urljoin(pkguri, scriptfile)
        if not fs.exists(scripturi):
            raise FileNotFoundError(f"Python script {scripturi} does not exist.")

        funcname = function["function"]

        # TODO: Importing the function as a check requires installing requirements.txt file
        # logger.debug(f"Attempting to import {scripturi}")
        # spec = importlib.util.spec_from_file_location(f"{pkg}.{scriptname}", scripturi)
        # module = importlib.util.module_from_spec(spec)
        # sys.modules["module.name"] = module
        # spec.loader.exec_module(module)
        # if not hasattr(module, funcname):
        #     raise ValueError(f"Python script {scriptname} does not have a function called {funcname}"

        functions.append(dict(pkgname=pkgname, scriptname=scriptname, name=funcname))

    return dict(name=name, servicename=servicename, functions=functions, interface=interface), dict(packages=packages)


def _check_src(src):
    """Checks that the source folder exists and has all required files

    Args:
        src (str): URI of the source folder
    """

    src = normalize_uri(src)

    # Init filesystem
    parsed_uri = urlparse(src)
    fs = fsspec.filesystem(parsed_uri.scheme)

    specuri = urljoin(src, SPEC_FILENAME)
    if not fs.exists(specuri):
        raise FileNotFoundError(f"Specification not found at {specuri}")

    pyproject_uri = urljoin(src, PYPROJECT_FILENAME)
    if not fs.exists(pyproject_uri):
        raise FileNotFoundError(f"pyproject.toml not found at {pyproject_uri}")

    pythonversion_uri = urljoin(src, PYTHONVERSION_FILENAME)
    if not fs.exists(pythonversion_uri):
        raise FileNotFoundError(f".python-version not found at {pythonversion_uri}")

    uvlock_uri = urljoin(src, UVLOCK_FILENAME)
    if not fs.exists(uvlock_uri):
        raise FileNotFoundError(f"uv.lock not found at {uvlock_uri}")

    enpkg_uri = urljoin(src, "src/enpkg")
    if not fs.exists(uvlock_uri):
        raise FileNotFoundError(f"Python source not found at {enpkg_uri}")

    return src


def _check_dest(dest, default=None):
    """Checks that the destination folder exists

    Args:
        dest (str): URI of the destination folder
        default (str, optional): Default folder to use if no destination was specified. Defaults to None.

    Raises:
        FileNotFoundError: If the folder does not exist
    """

    # Check destination
    parsed_uri = urlparse(dest)
    fs = fsspec.filesystem(parsed_uri.scheme)
    if dest is not None:
        dest = normalize_uri(dest)
        if not fs.exists(dest):
            fs.makedirs(dest)
            # raise FileNotFoundError(f"Directory {dest} does not exist.")
        return dest
    else:
        return default


def _render_templates(templates, dest, template_dict):
    """Renders jinja templates and writes them to dest

    Args:
        templates (list): A list of paths pointing to the templates to render
        dest (str): URI of directory to write the templates into
        template_dict (dict): A (flat) dictionary of the values being used for template rendering
    """

    fs = fsspec.filesystem(urlparse(dest).scheme)

    # Generating required files from jinja templates
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIRECTORY), autoescape=select_autoescape())
    for template_path in templates:

        # Create parent at dest if needed
        parent_template_path, template_file = os.path.split(template_path)
        parent_rendered_template_url = urljoin(dest, parent_template_path)
        fs.makedirs(parent_rendered_template_url, exist_ok=True)

        # Write template
        rendered_template = env.get_template(template_path).render(**template_dict)
        template_name, template_ext = os.path.splitext(template_file)
        rendered_template_url = urljoin(
            dest, os.path.join(parent_template_path, template_name) if template_ext == ".jinja" else template_path
        )

        print(dest, rendered_template_url, template_path, parent_template_path, template_name)
        with open(rendered_template_url, "w") as f:
            logging.debug(f"Writing {rendered_template_url}")
            f.write(rendered_template)


def _build_docker(dest, name):
    """Builds the docker image from dest

    Args:
        dest (str): Path to the docker context
        name (str): Name of the tool that will be used as tag for the container
    """
    with CwdContextManager(logger=logger):
        subprocess.run(["make", "docker"], cwd=dest, check=True)
    # image = docker.build(dockerfile_path, tags=name)

    imgid = docker.image.inspect(name).id
    logger.debug(f"Sucessfully build docker image {name} with id {imgid}")
    return imgid


def _lock_environment(src):
    """Creates the uv.lock file to pin the python environment by hash

    Args:
        src (str): URI pointing to the tool artifact directory
    """

    with CwdContextManager(logger=logger):
        subprocess.run(["uv", "sync"], cwd=src, check=True)


def _create_docker_context(src, dest=None, interface="args"):
    """Helper function to create a docker context for various interfaces

    Args:
        src (str): URI pointing to the tool artifact directory
        dest (str, optional): Where to create the container. If None, src will be used. Defaults to None.

    Returns:
        str: src normalized
        dest: dest normalized
        dict: Flat dictionary for template rendering
        dict: Flat dictionary of fully qualified uris
    """

    # Check that source files exist
    src = _check_src(src)

    # Parse spec and check that wrapper scripts exist
    template_dict, uri_dict = _parse_spec(src, interface=interface)

    # Check that destination folder exists
    dest = _check_dest(dest, default=src)

    # Pin the uv lockfile
    _lock_environment(src)

    # Copy project src
    fs = fsspec.filesystem(urlparse(dest).scheme)
    project_src = urljoin(src, "src")
    fs.cp(project_src, dest, recursive=True)

    # Copy extra barebone packages (if exist)
    project_extra = urljoin(src, "extra")
    if fs.exists(project_extra):
        fs.cp(project_extra, dest, recursive=True)

    # Copy data folder (if exist)
    project_data = urljoin(src, "data")
    if fs.exists(project_data):
        fs.cp(project_data, dest, recursive=True)

    # Copy pyproject.toml
    pyproject_toml = urljoin(src, PYPROJECT_FILENAME)
    fs.cp(pyproject_toml, dest)

    # Copy .python_version
    python_version = urljoin(src, PYTHONVERSION_FILENAME)
    fs.cp(python_version, dest)

    # Copy spec.json
    spec_json = urljoin(src, SPEC_FILENAME)
    fs.cp(spec_json, dest)

    # Copy uv.lock to dest
    uv_lock = urljoin(src, UVLOCK_FILENAME)
    fs.cp(uv_lock, dest)

    return src, dest, template_dict, uri_dict


def create_args_docker_context(src, dest=None):
    """Creates a docker context for a tool container with a args message passing interface

    Args:
        src (str): URI pointing to the tool artifact directory
        dest (str, optional): Where to create the container. If None, src will be used. Defaults to None.

    Returns:
        dict: Flat dictionary for template rendering
        dict: Flat dictionary of fully qualified uris
    """
    src, dest, template_dict, uri_dict = _create_docker_context(src, dest, interface="args")
    _render_templates(ARGS_TEMPLATES, dest, template_dict)

    return template_dict, uri_dict


def create_grpc_docker_context(src, dest=None):
    """Creates a docker context for a tool container with a grpc message passing interface

    Args:
        src (str): URI pointing to the tool artifact directory
        dest (str, optional): Where to create the container. If None, src will be used. Defaults to None.

    Returns:
        dict: Flat dictionary for template rendering
        dict: Flat dictionary of fully qualified uris
    """

    src, dest, template_dict, uri_dict = _create_docker_context(src, dest, interface="grpc")
    _render_templates(GRPC_TEMPLATES, dest, template_dict)

    return template_dict, uri_dict


def create_grpc(src, dest=None):
    """Creates a tool container with a grpc message passing interface

    Args:
        src (str): URI pointing to the tool artifact directory
        dest (str, optional): Where to create the container. If None, src will be used. Defaults to None.
    """
    template_dict, uri_dict = create_grpc_docker_context(src, dest)

    imgid = _build_docker(dest, template_dict["name"])

    return imgid, template_dict, uri_dict


def create_args(src, dest=None):
    """Creates a tool container with a cwl message passing interface

    Args:
        src (str): URI pointing to the tool artifact directory
        dest (str, optional): Where to create the container. If None, src will be used. Defaults to None.
    """

    template_dict, uri_dict = create_args_docker_context(src, dest)

    imgid = _build_docker(dest, template_dict["name"])

    return imgid, template_dict, uri_dict


def create(src, dest=None, interface="args"):
    """Creates a platform-compatible container of the tool located at src

    Args:
        src (str): URI pointing to the tool artifact directory
        dest (str, optional): Where to create the container. If None, src will be used. Defaults to None.
        interface (str, optional): The orchestration engine to be used. Either grpc or args. Defaults to args.

    Raises:
        FileNotFoundError: If the required files are not found
        ValueError: If the specification has an invalid syntax

    Returns:
        _type_: _description_
    """

    if interface == "grpc":
        return create_grpc(src, dest)

    if interface == "args":
        return create_args(src, dest)

    raise NotImplementedError(f"Generation with interface {interface} is currently not supported.")


def validate_toolspec(toolspec):
    """
    Validates the given toolspec against the jsonschema definition for tool specs.

    Args:
        toolspec (dict): The toolspec to be validated.

    Returns:
        bool: True if the toolspec is valid, False otherwise.
    """
    try:
        validate(toolspec)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, required=True)
    parser.add_argument("-o", type=str)
    parser.add_argument("--interface", type=str, default="args")
    args = parser.parse_args()
    create(args.i, args.o, interface=args.interface)
