"""Wrapper functions for scikit_learn metrics"""

import argparse
import json
import numpy as np
import pickle
import logging
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    matthews_corrcoef,
    mean_squared_error,
    confusion_matrix,
)

from mki_barebone_io.ndarray import load_ndarray
from mki_barebone_io.dict import store_dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Dictionary mapping metric names to functions
METRICS = {
    "accuracy": accuracy_score,
    "precision": precision_score,
    "recall": recall_score,
    "f1": f1_score,
    "roc_auc": roc_auc_score,
    "mcc": matthews_corrcoef,
    "mse": mean_squared_error,
    "specificity": None,  # Placeholder, computed separately
    "balanced_accuracy": None,  # Placeholder, computed separately
    "tp": None,
    "fp": None,
    "tn": None,
    "fn": None,  # Placeholders for confusion matrix values
}


def compute_metric(y_true: np.ndarray, y_pred: np.ndarray, metric: str) -> float:
    """Computes the selected evaluation metric.

    Args:
        y_true (np.ndarray): Ground truth labels.
        y_pred (np.ndarray): Predicted labels.
        metric (str): The metric to compute.

    Returns:
        float: Computed metric value.
    """
    if metric not in METRICS:
        raise ValueError(f"Invalid metric '{metric}'. Choose from: {', '.join(METRICS.keys())}")

    # Compute confusion matrix components
    if metric in {"tp", "fp", "tn", "fn", "specificity", "balanced_accuracy"}:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    if metric == "tp":
        return int(tp)
    elif metric == "fp":
        return int(fp)
    elif metric == "tn":
        return int(tn)
    elif metric == "fn":
        return int(fn)
    elif metric == "specificity":
        return tn / (tn + fp) if (tn + fp) > 0 else None
    elif metric == "balanced_accuracy":
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else None
        specificity = tn / (tn + fp) if (tn + fp) > 0 else None
        return (sensitivity + specificity) / 2 if sensitivity is not None and specificity is not None else None

    # Compute standard metrics
    return METRICS[metric](y_true, y_pred)


def _scikit_metrics_wrapper(execution_msg: dict, metric_name: str) -> dict:
    """Wraps scikit-learn.metrics function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.
        metric_name (str): Name of the metric to execute

    Returns:
        dict: Execution message with computed metric results.
    """

    # Get URI info from execution message
    y_true_artifact = execution_msg["input"][0]
    y_pred_artifact = execution_msg["input"][1]
    output_artifact = execution_msg["output"][0]

    # Load inputs
    y_true = load_ndarray(y_true_artifact)
    y_pred = load_ndarray(y_pred_artifact)

    # Compute the selected metric
    results = compute_metric(y_true, y_pred, metric_name)
    logger.debug(f"Computed {metric_name}: {results}")

    # Store the results
    output_artifact = store_dict({metric_name: results}, output_artifact)

    # Return execution message
    return dict(
        func=f"{metric_name}_wrapper",
        input=execution_msg["input"],
        output=[output_artifact],
        meta=execution_msg["meta"],
    )


def accuracy_wrapper(execution_msg: dict) -> dict:
    """Wraps scikit-learn accuracy function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "accuracy")


def precision_wrapper(execution_msg: dict) -> dict:
    """Wraps scikit-learn precision function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "precision")


def recall_wrapper(execution_msg: dict) -> dict:
    """Wraps scikit-learn recall function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "recall")


def f1_wrapper(execution_msg: dict) -> dict:
    """Wraps scikit-learn f1 function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "f1")


def roc_auc_wrapper(execution_msg: dict) -> dict:
    """Wraps scikit-learn roc auc function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "roc_auc")


def mcc_wrapper(execution_msg: dict) -> dict:
    """Wraps scikit-learn mcc function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "mcc")


def mse_wrapper(execution_msg: dict) -> dict:
    """Wraps scikit-learn mse function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "mse")


def specificity_wrapper(execution_msg: dict) -> dict:
    """Wraps scikit-learn specificity function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "specificity")


def balanced_accuracy_wrapper(execution_msg: dict) -> dict:
    """Wraps scikit-learn specificity function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "balanced_accuracy")


def tp_wrapper(execution_msg: dict) -> dict:
    """Wraps tp function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "tp")


def fp_wrapper(execution_msg: dict) -> dict:
    """Wraps scikit-learn specificity function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "fp")


def tn_wrapper(execution_msg: dict) -> dict:
    """Wraps tn function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "tn")


def fn_wrapper(execution_msg: dict) -> dict:
    """Wraps fn function for barebone execution.

    Args:
        execution_msg (dict): Execution message containing input/output URIs.

    Returns:
        dict: Execution message with computed metric results.
    """

    return _scikit_metrics_wrapper(execution_msg, "fn")


def load_model(model_path: str, X_test: np.ndarray) -> np.ndarray:
    """Loads a trained model from a pickle file and makes predictions.

    Args:
        model_path (str): Path to the trained model file (.pkl).
        X_test (np.ndarray): Feature dataset to make predictions.

    Returns:
        np.ndarray: Model predictions.
    """
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model.predict(X_test)


def main():
    """Parses command-line arguments, loads inputs, and computes the metric.

    Raises:
        ValueError: If neither `--pred` nor `--model` and `--X_test` are provided.
    """
    parser = argparse.ArgumentParser(description="Compute an evaluation metric for a model.")
    parser.add_argument("--true", type=str, required=True, help="Path to true labels (JSON file).")
    parser.add_argument("--pred", type=str, help="Path to predicted labels (JSON file).")
    parser.add_argument("--model", type=str, help="Path to trained model (Pickle file).")
    parser.add_argument("--X_test", type=str, help="Path to test data (JSON file, if using model).")
    parser.add_argument(
        "--metric",
        type=str,
        default="accuracy",
        choices=METRICS.keys(),
        help="Metric to compute (default: accuracy).",
    )

    args = parser.parse_args()

    # Load ground truth labels
    y_true = load_json(args.true)

    # Use either a model or precomputed predictions
    if args.model and args.X_test:
        X_test = load_json(args.X_test)
        y_pred = load_model(args.model, X_test)
    elif args.pred:
        y_pred = load_json(args.pred)
    else:
        raise ValueError("Either --pred or (--model and --X_test) must be provided.")

    # Compute the selected metric
    result = compute_metric(y_true, y_pred, args.metric)

    # Output JSON result
    print(json.dumps({args.metric: result}))


if __name__ == "__main__":
    main()
