{
  "cwlVersion": "v1.2",
  "class": "Workflow",
  "inputs": {
    "func": {
      "type": "string"
    },
    "input_uri": {
      "type": {
        "type": "array",
        "items": "File"
      },
      "default": ["data/features.json"]
    },
    "output_uri": {
      "type": {
        "type": "array",
        "items": "string"
      },
      "default": ["results.json"]
    }
  },
  "outputs": {
    "final_outputs": {
      "type": {
        "type": "array",
        "items": "File"
      },
      "outputSource": "process_step/output_files"
    }
  },
  "steps": {
    "process_step": {
      "run": "tool.cwl",
      "in": {
        "func": "func",
        "input_uri": "input_uri",
        "output_uri": "output_uri"
      },
      "out": ["output_files"]
    }
  }
}
