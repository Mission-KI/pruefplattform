{
  "cwlVersion": "v1.2",
  "class": "CommandLineTool",
  "requirements": {
    "DockerRequirement": {
      "dockerPull": "mocktool"
    }
  },
  "baseCommand": [ "python","-u","/home/user/src/enpkg/main.py" ],
  "inputs": {
    "func": {
      "type": "string",
      "inputBinding": {
        "prefix": "--func"
      }
    },
    "input_uri": {
      "type": {
        "type": "array",
        "items": "File"
      },
      "inputBinding": {
        "prefix": "--input_uri"
      }
    },
    "output_uri": {
      "type": {
        "type": "array",
        "items": "string"
      },
      "inputBinding": {
        "prefix": "--output_uri"
      }
    }
  },
  "outputs": {
    "output_files": {
      "type": {
        "type": "array",
        "items": "File"
      },
      "outputBinding": {
        "glob": "$(inputs.output_uri)"
      }
    }
  },
  "stdout": "processing.log"
}