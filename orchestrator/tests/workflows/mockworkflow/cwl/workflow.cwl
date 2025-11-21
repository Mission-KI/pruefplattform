{
  "cwlVersion": "v1.2",
  "class": "Workflow",
  "requirements": {
    "MultipleInputFeatureRequirement": {}
  },
  "inputs": {
    "model_func": {
      "type": "string"
    },
    "model_input_uri": {
      "type": {
        "type": "array",
        "items": "File"
      }
    },
    "model_output_uri": {
      "type": {
        "type": "array",
        "items": "string"
      },
      "default": ["mock_predictions.json"]
    },
    "tool_func": {
      "type": "string"
    },
    "tool_input_uri": {
      "type": {
        "type": "array",
        "items": "File"
      },
      "default": ["mock_predictions.json", "mock_groundtruth.json"]
    },
    "tool_output_uri": {
      "type": {
        "type": "array",
        "items": "string"
      },
      "default": ["mock_results.json"]
    }
  },
  "outputs": {
    "model_outputs": {
      "type": {
        "type": "array",
        "items": "File"
      },
      "outputSource": "model_step/output_files"
    },
    "final_outputs": {
      "type": {
        "type": "array",
        "items": "File"
      },
      "outputSource": "tool_step/output_files"
    }
  },
  "steps": {
    "model_step": {
      "run": "model.cwl",
      "in": {
        "func": "model_func",
        "input_uri": "model_input_uri",
        "output_uri": "model_output_uri"
      },
      "out": ["output_files"]
    },
    "tool_step": {
      "run": "tool.cwl",
      "in": {
        "func": "tool_func",
        "input_uri": {
          "source": ["model_step/output_files", "tool_input_uri"],
          "linkMerge": "merge_flattened"
        },
        "output_uri": "tool_output_uri"
      },
      "out": ["output_files"]
    }
  }
}
