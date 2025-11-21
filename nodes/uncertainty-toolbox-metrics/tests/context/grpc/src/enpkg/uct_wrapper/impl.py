from functools import wraps
import logging
from typing import Optional

import os
import jsonref
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from mki_barebone_io.arrow import load_arrow, store_arrow, parse_schema
from mki_barebone_io.dict import load_dict
import numpy as np
import pyarrow as pa
import uncertainty_toolbox as uct

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TOOL_WORKDIR = os.getenv("TOOL_WORKDIR", default="")
with open(os.path.join(TOOL_WORKDIR, "spec.json"), "r", encoding="utf8") as fp:
    toolspec: dict = jsonref.loads(fp.read())


def wrap_metric(rename: Optional[str] = None):
    """
    Decorator to wrap a metric from the uncertainty-toolbox library to be callable
    via gRPC when built into a plattform-compatible container.
    """

    def decorator(func):

        @wraps(func)
        def func_apply(execution_msg: dict) -> dict:

            # get the part of the spec that declares the called metric function
            function_spec = toolspec["functions"][func.__name__ if rename is None else rename]

            # parse arrow schemas for function argument from input section of function spec
            prediction_schema = parse_schema(function_spec["inputs"][0]["schema"]["fields"])
            label_schema = parse_schema(function_spec["inputs"][1]["schema"]["fields"])

            # parse the configuration file of the metric function
            config = load_dict(execution_msg["input"][2])
            try:
                config_schema = function_spec["inputs"][2]["schema"]
                validate(config, config_schema)
            except ValidationError as e:
                raise ValueError(f"Invalid config spec: {str(e)}")

            # parse the arrow schema for function ouotput
            metric_schema = parse_schema(function_spec["outputs"][0]["schema"]["fields"])

            metrics_spec = execution_msg["output"][0]

            # load the input arguments from the given arrow files
            prediction_batches = load_arrow(execution_msg["input"][0], prediction_schema)
            label_batches = load_arrow(execution_msg["input"][1], label_schema)

            if len(prediction_batches) != len(label_batches):
                raise ValueError("Number of prediction batches must equal the number of label batches")

            metrics = []
            # iterate over all batches
            for predictions, labels in zip(prediction_batches, label_batches):
                # calculate the metric value for the given batch
                metric_value = func(
                    predictions["prediction_mean"].to_numpy(),
                    predictions["prediction_std"].to_numpy(),
                    labels["label"].to_numpy(),
                    **config,
                )
                metrics.append(pa.table({"metric_value": np.array([metric_value])}, schema=metric_schema))

            # store the calulated metric value(s)
            metrics_spec = store_arrow(metrics, metrics_spec, metric_schema)

            # return dict execution message
            return dict(
                func=execution_msg["func"],
                input=execution_msg["input"],
                output=[metrics_spec],
                meta=execution_msg["meta"],
            )

        return func_apply

    return decorator


# average calibration
mean_absolute_calibration_error = wrap_metric()(uct.mean_absolute_calibration_error)
root_mean_squared_calibration_error = wrap_metric()(uct.root_mean_squared_calibration_error)
miscalibration_area = wrap_metric()(uct.miscalibration_area)


def expected_calibration_error(execution_msg: dict) -> dict:
    return mean_absolute_calibration_error(execution_msg)


# proper scoring rules
interval_score = wrap_metric()(uct.interval_score)
check_score = wrap_metric()(uct.check_score)


def negative_log_likelihood(execution_msg: dict) -> dict:
    return wrap_metric(rename="negative_log_likelihood")(uct.nll_gaussian)(execution_msg)


def continuous_ranked_probability_score(execution_msg: dict) -> dict:
    return wrap_metric(rename="continuous_ranked_probability_score")(uct.crps_gaussian)(execution_msg)


# sharpness (expected standard deviation)
def expected_standard_deviation(execution_msg: dict) -> dict:
    function_spec = toolspec["functions"]["expected_standard_deviation"]

    input_schema = parse_schema(function_spec["inputs"][0]["schema"]["fields"])
    metric_schema = parse_schema(function_spec["outputs"][0]["schema"]["fields"])

    metrics_spec = execution_msg["output"][0]

    input_batches = load_arrow(execution_msg["input"][0], input_schema)
    metrics = []
    # iterate over all batches
    for batch in input_batches:
        # calculate the expected standard deviation for the given batch
        metric_value = uct.sharpness(batch["prediction_std"].to_numpy())
        metrics.append(pa.table({"metric_value": np.array([metric_value])}, schema=metric_schema))

    # store the calulated metric value(s)
    metrics_spec = store_arrow(metrics, metrics_spec, metric_schema)

    # return dict execution message
    return dict(
        func=execution_msg["func"],
        input=execution_msg["input"],
        output=[metrics_spec],
        meta=execution_msg["meta"],
    )


# TODO
# # adversarial group calibration
# mean_absolute_adversarial_group_calibration_error = wrap_metric()(
#     partial(uct.adversarial_group_calibration, cali_type="mean_abs")
# )
# root_mean_squared_adversarial_group_calibration_error = wrap_metric()(
#     partial(uct.adversarial_group_calibration, cali_type="root_mean_sq")
# )
