import fsspec
import logging
import os
from platform import system
import re
import subprocess
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional
from time import sleep
from pathlib import Path

import pytest
from python_on_whales import DockerClient
from python_on_whales.components.compose.models import ComposeConfig

from tests.utils import CwdContextManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Due to file permission issues with colima, the temporary directory needs to be created differently under MacOS
if system() == "Darwin":
    temp_base = os.getcwd()
else:
    temp_base = None  # Use the system default


class ComposeContextManager:
    """A context manager for a Docker client to clean up if anything fails"""

    def __init__(self, docker, timeout=5):
        self._docker = docker
        self.timeout = timeout

    def __enter__(self):
        logger.debug("docker compose up")
        try:
            self._docker.compose.up(detach=True, wait_timeout=self.timeout)
        except Exception:
            logger.debug("docker compose up did not complete correctly. Aborting.")
        return self._docker

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug("docker compose down")
        self._docker.compose.down()


def full_image_name(image_name: str) -> str:
    """
    Returns the full image name, including the tag, if not already provided.

    Args:
        image_name (str): The name of the image, potentially without a tag.

    Returns:
        str: The full image name, including the tag (defaults to ":latest" if not provided).
    """
    # Check, if image name contains a tag:
    if re.search(r":[a-zA-Z\d_][a-zA-Z\d_.-]{0,127}$", image_name) is not None:
        # full name (incl. tag) given, nothing to do
        return image_name
    return f"{image_name}:latest"


def image_name_to_id_map(docker: DockerClient) -> Dict[str, str]:
    """
    Generates a dictionary mapping available image tags to their corresponding image IDs.

    Args:
        docker (DockerClient): A client for interacting with Docker, used to retrieve image information.

    Returns:
        Dict[str, str]: A dictionary where keys are image tags and values are their corresponding image IDs.
    """
    return dict(
        item
        for inner_list in [
            [(tag, image.id) for tag in image.repo_tags]
            for image in docker.images()
            if image.repo_tags
        ]
        for item in inner_list
    )


def services_running(docker: DockerClient, config: ComposeConfig) -> List[bool]:
    """
    Checks if services defined in the provided compose config are running.

    Args:
        docker (DockerClient): A client for interacting with Docker.
        config (ComposeConfig): The compose configuration containing service definitions.

    Returns:
        List[bool]: A list of boolean values indicating whether each service is running.
    """
    # get the image IDs for all services in the config that should be running
    image_name_to_id = image_name_to_id_map(docker)
    service_image_ids = [
        image_name_to_id.get(full_image_name(svc.image))
        for svc in config.services.values()
    ]
    # check if containers based on these images are actually running
    running_image_ids = [container.image for container in docker.ps()]
    return [img_id in running_image_ids for img_id in service_image_ids]


def available_images(docker: DockerClient, config: ComposeConfig) -> List[str]:
    """
    Retrieves a list of image names that have been built, based on the provided Docker Compose configuration.

    Args:
        docker (DockerClient): A client for interacting with Docker, used to retrieve image information.
        config (ComposeConfig): The Docker Compose configuration containing service definitions.

    Returns:
        List[str]: A list of image names that have been built.
    """
    image_name_to_id = image_name_to_id_map(docker)
    all_image_names = [full_image_name(svc.image) for svc in config.services.values()]
    return [name for name in all_image_names if name in image_name_to_id]


def tool_workflow_compose(
    tests_dir: str,
    context_dir: str,
    orch_context_dir: str,
    compose_config_filename: str,
    tool_container_dirname: str,
    tool_container_name: str,
    test_func: callable,
    inputs: Optional[List[str]] = None,
) -> None:
    """Tests a tool workflow by bringing up a Docker Compose configuration,
    checking that all services are running and verifying the that the tool
    service is healthy and produced the expected output.

    Args:
        tests_dir (str): Path to the tests directory of the node that contains the workflow spec
        context_dir (str): Path to the node context directory
        orch_context_dir (str): Path to the orchestrator context directory
        compose_config_filename (str): Filename of the docker compose config to use.
        tool_container_dirname (str): Directory name of the directory containing the tool image context.
        tool_container_name (str): Name of the tool container image
        test_func (callable): A callable of signature (DockerClient, DockerContainer, str) that tests
                            whether the launched containers are functioning properly
        inputs (list, optional): A list of paths of input files
    Raises:
        StopIteration: If container does not exist.
    """
    with TemporaryDirectory(dir=temp_base) as temp_dir:
        fs = fsspec.filesystem("file")
        os.chmod(
            temp_dir, 511
        )  # make folder world accessible to prevent issues of namespace remapping

        input_folder = os.path.join(temp_dir, "inputs")
        result_folder = os.path.join(temp_dir, "results")

        os.makedirs(input_folder)
        os.makedirs(result_folder)

        # create environment file for mock workflow:
        env_file = os.path.join(temp_dir, ".env")
        with open(env_file, "w", encoding="utf8") as fh:
            fh.write(f"image_name={tool_container_name}\n")
            fh.write(f"inputs={input_folder}\n")
            fh.write(f"results={result_folder}\n")

        if inputs:
            for filepath in inputs:
                fs.cp(filepath, input_folder)

        compose_file = os.path.join(temp_dir, compose_config_filename)
        fs.copy(
            os.path.join(tests_dir, "workflow", "compose", compose_config_filename),
            compose_file,
        )

        # Check if a service is already running
        compose_config_name, _ = os.path.splitext(compose_config_filename)
        compose_project_name = f"{compose_config_name}_{tool_container_dirname}"
        docker = DockerClient(
            compose_files=[compose_file], compose_project_name=compose_project_name
        )
        config = docker.compose.config()
        if any(services_running(docker, config)):
            logger.debug(
                "Services are already running, shutting them down via compose ..."
            )
            docker.compose.down()
        for image in available_images(docker, config):
            docker.image.remove(image)

        # Rebuild tool
        tool_dir = os.path.join(context_dir, "grpc")
        if not os.path.exists(tool_dir):
            raise Exception(
                f"Context to tool node could not be found in {tool_dir}. Please copy the tool context to tool_dir={tool_dir}"
            )
        with CwdContextManager():
            subprocess.run(["make", "docker"], cwd=tool_dir, check=True)

        # Rebuild orchestrator
        if not os.path.exists(orch_context_dir):
            raise Exception(
                f"Context to orchestrator could not be found in {orch_context_dir}. Please copy the orchestrator context to orch_context_dir={orch_context_dir}"
            )
        with CwdContextManager():
            subprocess.run(["make", "docker"], cwd=orch_context_dir, check=True)

        with ComposeContextManager(docker, timeout=60):
            try:
                sleep(5)  # Wait for the orchestrator to send message
                assert all(services_running(docker, config))
                tool_container = next(
                    container
                    for container in docker.ps()
                    if container.name == tool_container_name
                )
                # check that the service is healthy
                assert tool_container.state.health.status == "healthy"

                test_func(docker, tool_container, temp_dir)

            except StopIteration as e:
                logger.exception(
                    f"Failed to find running container named {tool_container_name}."
                )
                raise e


def tool_workflow_cwl(node_workflow_dir: str, test_func: callable) -> None:
    """Tests a tool workflow by running a cwl configuration and verifying the that the workflow produced the expected output.

    Args:
        node_workflow_dir (str): Path to the directory containing the cwl config files to use. Has to contain a workflow.cwl file and a job.json file
        test_func (callable): A callable of signature (str) that tests
                            whether the launched containers are functioning properly

    Raises:
        StopIteration: If container does not exist.
    """

    with TemporaryDirectory(dir=temp_base) as temp_dir:
        os.chmod(
            temp_dir, 511
        )  # make folder world accessible to prevent issues of namespace remapping

        result_folder = os.path.join(temp_dir, "results")
        os.makedirs(result_folder)

        cwl_dir = os.path.join(node_workflow_dir, "cwl")
        assert os.path.exists(cwl_dir), f"Missing workflow dir: {cwl_dir}"

        with CwdContextManager():

            subprocess.run(
                [
                    "uv",
                    "run",
                    "--extra",
                    "dev",
                    "cwltool",
                    "--outdir",
                    result_folder,
                    "workflow.cwl",
                    "job.json",
                ],
                cwd=cwl_dir,
                check=True,
            )

        test_func(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])
