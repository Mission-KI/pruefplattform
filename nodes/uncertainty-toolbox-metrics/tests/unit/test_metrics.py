from functools import wraps
import logging
from math import isclose
import os
from sys import float_info
from tempfile import TemporaryDirectory

import fsspec
import pytest

from mki_barebone_io.arrow import load_arrow, parse_schema
import uct_wrapper.impl as tool
from uct_wrapper.impl import toolspec


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

test_values = {
    "mean_absolute_calibration_error": [0.08892045454545457, 0.0793308080808081],
    "expected_calibration_error": [0.08892045454545457, 0.0793308080808081],
    "root_mean_squared_calibration_error": [0.10451771654791632, 0.11035530503862676],
    "miscalibration_area": [0.08966595548862116, 0.07953515798960081],
    "interval_score": [4.102095805367317, 3.3124229317776464],
    "check_score": [0.2986608673839315, 0.282393206264176],
    "negative_log_likelihood": [19.950819262056484, 2.1526683629843086],
    "continuous_ranked_probability_score": [0.5931034954616157, 0.5595516824034207],
    "expected_standard_deviation": [0.9417631543603469, 0.8300076626704962],
}


def wrap_uncertainty_metric():
    """
    Decorator to generate a test for a given metric from the uncertainty-toolbox-metrics package.
    """

    def decorator(func):

        @wraps(func)
        def func_apply(config: str) -> None:
            func_name = func.__name__
            test_data_path = os.path.join("tests", "data")
            test_predictions_loc = dict(location={"uri": os.path.join(test_data_path, "predictions.arrow")})
            test_labels_loc = dict(location={"uri": os.path.join(test_data_path, "labels.arrow")})
            test_config_loc = dict(location={"uri": os.path.join(test_data_path, config)})

            # parse the pyarrow schema fro the output section of the function spec
            metric_schema = parse_schema(toolspec["functions"][func_name]["outputs"][0]["schema"]["fields"])

            with TemporaryDirectory() as tempdir:
                result_file = os.path.join(tempdir, "metric_values.arrow")
                metric_values_loc = dict(location=dict(uri=result_file))
                execution_msg = dict(
                    func=func_name,
                    input=[test_predictions_loc, test_labels_loc, test_config_loc],
                    output=[metric_values_loc],
                    meta={"execution_name": "test_execution"},
                )
                execution_msg = func(execution_msg)

                fs = fsspec.filesystem("file")
                assert fs.exists(result_file), f"{result_file} does not exist."
                metric_values = load_arrow(dict(location={"uri": result_file}), metric_schema)
                eps = float_info.epsilon
                for calc_value, test_value in zip(metric_values, test_values[func_name]):
                    assert isclose(calc_value["metric_value"][0].as_py(), test_value, rel_tol=eps, abs_tol=eps)

        return func_apply

    return decorator


def test_mean_absolute_calibration_error() -> None:
    wrap_uncertainty_metric()(tool.mean_absolute_calibration_error)("config_A.json")


def test_expected_calibration_error() -> None:
    wrap_uncertainty_metric()(tool.expected_calibration_error)("config_A.json")


def test_root_mean_squared_calibration_error() -> None:
    wrap_uncertainty_metric()(tool.root_mean_squared_calibration_error)("config_A.json")


def test_miscalibration_area() -> None:
    wrap_uncertainty_metric()(tool.miscalibration_area)("config_A.json")


def test_interval_score() -> None:
    wrap_uncertainty_metric()(tool.interval_score)("config_B.json")


def test_check_score() -> None:
    wrap_uncertainty_metric()(tool.check_score)("config_B.json")


def test_negative_log_likelihood() -> None:
    wrap_uncertainty_metric()(tool.negative_log_likelihood)("config_B.json")


def test_continuous_ranked_probability_score() -> None:
    wrap_uncertainty_metric()(tool.continuous_ranked_probability_score)("config_B.json")


def test_expected_standard_deviation() -> None:
    """
    Tests the expected standard deviation uncertainty metric function.
    """
    test_data_path = os.path.join("tests", "data")
    test_input_loc = dict(location={"uri": os.path.join(test_data_path, "standard_deviations.arrow")})

    # parse the pyarrow schema fro the output section of the function spec
    metric_schema = parse_schema(toolspec["functions"]["expected_standard_deviation"]["outputs"][0]["schema"]["fields"])

    with TemporaryDirectory() as tempdir:
        result_file = os.path.join(tempdir, "metric_values.arrow")
        metric_values_loc = dict(location=dict(uri=result_file))
        execution_msg = dict(
            func="expected_standard_deviation",
            input=[test_input_loc],
            output=[metric_values_loc],
            meta={"execution_name": "test_execution"},
        )
        execution_msg = tool.expected_standard_deviation(execution_msg)

        fs = fsspec.filesystem("file")
        assert fs.exists(result_file), f"{result_file} does not exist."
        metric_values = load_arrow(dict(location={"uri": result_file}), metric_schema)
        eps = float_info.epsilon
        for calc_value, test_value in zip(metric_values, test_values["expected_standard_deviation"]):
            assert isclose(calc_value["metric_value"][0].as_py(), test_value, rel_tol=eps, abs_tol=eps)


if __name__ == "__main__":
    pytest.main([__file__])
