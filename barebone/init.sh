#!/bin/bash

function question {
    echo -n "$1 " >&2
    local ANSWER
    read ANSWER
    echo $ANSWER
}

function getOS {
    OS=${OSTYPE//[0-9.-]*/}
    case "$OS" in
      linux)  echo 'linux' ;;
      darwin) echo 'macos' ;;
      msys)   echo 'win' ;;
      *)      echo 'UNKNOWN' ;;
    esac
}

function isOkForBarebone {
    [ $(getOS) == 'linux' ]
}

function isDefined {
    local VAR="$1"; shift
    local MSG="$1"; shift

    local VAL="${!VAR}"
    if [ "${VAL}" == '' ]
    then
        echo "$MSG Exit 12"
        exit 12
    fi
}


echo 'Initializing a project with data for a container compatible with the MISSION KI platform'

ROOT_DIR=$(question 'provide the path to a (not existing) root directory:')
isDefined ROOT_DIR 'the root directory is invalid.'

if [ -e "$ROOT_DIR" ]; then
    echo "The file or directory \"$ROOT_DIR\" does exist. This would be dangerous. Exit 12"
    exit 12
fi

mkdir -p $ROOT_DIR
cd $ROOT_DIR
if [ $? -ne 0 ]; then
    echo "Could not create root directory \"$ROOT_DIR\". Exit 12"
    exit 12
fi

WHICH=$(which uv)
if [[ "${WHICH}" == '' ]]
then
    echo 'the command "uv" is not available. Please install it before you write Python code.'
    echo 'follow the simple instructions on https://docs.astral.sh/uv/getting-started/installation/'
    exit 12 # to avoid debug problems for the user
fi
WHICH=$(which git)
if [[ "${WHICH}" == '' ]]
then
    echo 'the command "git" is not available. Please install git'
    exit 12 # to avoid debug problems for the user
fi
WHICH=$(which docker)
if [[ "${WHICH}" == '' ]]
then
    echo '"docker" is not available. Please install docker. There are many possibilities.'
    echo 'you may follow https://docs.docker.com/engine/install/ or https://docs.docker.com/desktop/'
    exit 12 # to avoid debug problems for the user
fi

MODULE=$(question 'provide the name of the module (often similiar to the name of the root directory):')
isDefined MODULE 'the module name is invalid.'

mkdir -p src/enpkg/$MODULE docs tests

cat >README.md <<.EOF ###################################################################
-to be written-
.EOF
echo 'please write README.md'
cat >LICENSE <<.EOF #####################################################################
-to be written-
.EOF
echo 'please write LICENSE'
cat >pyproject.toml <<.EOF ##############################################################
[project]
name = "$MODULE"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "fsspec>=2025.3.0",
    "grpcio-tools>=1.71.0"
]
.EOF
echo 'please edit pyproject.toml and add at least your dependencies.'
echo 'then run "uv sync"'
echo 'alternatively you can use "uv add <dependency>"'
cat >.gitignore <<.EOF ##################################################################
# Ignore virtual environments
**/.venv/

# Ignore Python cache files
**/__pycache__/
**/.pytest_cache/

# Ignore test-generated files and results
tests/**/results/
tests/generated_*/
.EOF
cat >spec.json <<.EOF
{
    "id": {
        "domain": "local",
        "name": "$MODULE"
    },
    "description": "<tool-description>",
    "functions": {
        "<function1>": {
            "project": "<...>",
            "package": {
                "name": "$MODULE",
                "path": "src/enpkg/$MODULE"
            },
            "script": "hello_world.py",
            "function": "<function-name>",
            "inputs": [],
            "outputs": []
        },
        "<function2>": { ... }
    },
    "build": {
        "requirements": ""
    }
}
.EOF
echo 'please edit spec.json to define the functions your tool should provide.'
mkdir -p src/enpkg/$MODULE
cat >src/enpkg/$MODULE/hello_world.py <<.EOF
def fourtytwo():
    return 42


def barebone_wrapper(func, execution_msg):
    """Function that wraps tool functionality

    Args:
        execution_msg (dict): An ExecutionMessage containing information about the inputs for and wanted outputs
        of the tool function

    Returns:
        dict: An ExecutionMessage containing information about the inputs and outputs of the tool function
    """

    result = func()
    return None


def fourtytwo_wrapper(execution_msg: dict) -> dict:
    """Function that wraps a function returning fourtytwo

    Args:
        execution_msg (dict): An ExecutionMessage containing information about the inputs for and wanted outputs
        of the tool function

    Returns:
        dict: An ExecutionMessage containing information about the inputs and outputs of the tool function
    """

    return barebone_wrapper(fourtytwo, execution_msg)
.EOF
cat >.python-version <<.EOF
3.9

.EOF
git init 2>/dev/null