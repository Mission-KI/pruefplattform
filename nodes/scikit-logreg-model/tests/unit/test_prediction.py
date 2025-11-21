import json
import logging
import os
from tempfile import TemporaryDirectory

import fsspec
import pytest

from mki_barebone_io.dict import load_dict
from logreg_model_wrapper.impl import logreg_model, predict_wrapper


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@pytest.mark.scikit_logreg_model
@pytest.mark.unit
def test_prediction(node_test_dir) -> None:
    """
    Tests the prediction functionality of the logistic regression model by comparing
    its predictions with pre-computed test predictions.

    Args:
    None

    Returns:
    None
    """
    test_data_path = os.path.join(node_test_dir, "data")
    test_features_loc = dict(
        location=dict(uri=os.path.join(test_data_path, "features.json"))
    )
    test_predictions_loc = dict(
        location=dict(uri=os.path.join(test_data_path, "predictions.json"))
    )

    features = load_dict(test_features_loc)
    test_predictions = load_dict(test_predictions_loc)
    model_predictions = logreg_model.predict(features)
    assert model_predictions.tolist() == test_predictions

    with TemporaryDirectory() as tempdir:
        result_file = os.path.join(tempdir, "results.json")
        model_predictions_loc = dict(location=dict(uri=result_file))
        execution_msg = dict(
            func="predict_wrapper",
            input=[test_features_loc],
            output=[model_predictions_loc],
            meta={"execution_name": "test_execution"},
        )
        execution_msg = predict_wrapper(execution_msg)

        fs = fsspec.filesystem("file")
        assert fs.exists(result_file), f"{result_file} does not exist."
        with fs.open(result_file, "r") as fh:
            assert (
                json.load(fh) == test_predictions
            ), f"Function value returned must be {test_predictions}"


if __name__ == "__main__":
    pytest.main([__file__])
