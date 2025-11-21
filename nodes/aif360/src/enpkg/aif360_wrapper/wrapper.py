import logging

import pandas as pd

from mki_barebone_io.dict import load_dict, store_dict
from mki_barebone_io.dataframe import load_dataframe

from aif360.metrics import BinaryLabelDatasetMetric
from aif360.datasets import BinaryLabelDataset

from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _parse_config(config):
    # Which value of the label is favorable
    favorable_label = config.get("favorable_label", 1.0)

    # Which value of the label is unfavorable
    unfavorable_label = config.get("unfavorable_label", 0.0)

    # Name of the label column
    label_name = config.get("label_name", "default")

    # Which column corresponds to a protected attribute
    protected_attribute_names = config.get("protected_attribute_names")

    # From the protected attributes, which values are considered priviledged (default all with value 1)
    _default_priviledged_groups = [
        {protected_attribute_name: 1} for protected_attribute_name in protected_attribute_names
    ]
    privileged_groups = config.get("privileged_groups", _default_priviledged_groups)

    # From the protected attributes, which values are considered unpriviledged (default all with value 0)
    _default_unpriviledged_groups = [
        {protected_attribute_name: 0} for protected_attribute_name in protected_attribute_names
    ]
    unpriviledged_groups = config.get("unpriviledged_groups", _default_unpriviledged_groups)

    return (
        favorable_label,
        unfavorable_label,
        label_name,
        protected_attribute_names,
        privileged_groups,
        unpriviledged_groups,
    )


def aif360_binary_label_dataset_metric_wrapper(execution_msg: dict, func) -> dict:
    """Function that wraps tool functionality

    Args:
        execution_msg (dict): An ExecutionMessage containing information about the inputs for and wanted outputs
        of the tool function

    Returns:
        dict: An ExecutionMessage containing information about the inputs and outputs of the tool function
    """

    # get uri info from execution message
    artifact_df = execution_msg["input"][0]
    artifact_config = execution_msg["input"][1]
    artifact_result = execution_msg["output"][0]

    # All columns in dataframe need to be numerical, NA must not appear
    # csv must contain column names in header
    df = load_dataframe(artifact_df)
    config = load_dict(artifact_config)

    result = func(df, config)
    logger.debug(f"Computed result {result}")

    # store results, the format needs to be specified in the execution node manifest model.json
    artifact_result = store_dict(result, artifact_result)

    # return dict execution message
    return dict(
        func=execution_msg["func"],
        input=execution_msg["input"],
        output=[artifact_result],
        meta=execution_msg["meta"],
    )


def preprocess_dataframe(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Preprocess the DataFrame to be compatible with BinaryLabelDataset.

    - Encodes categorical variables
    - Fills missing values (set config key missing_handling to "fill" (default) or "drop")
    - Ensures numeric types for all columns
    """
    df = df.copy()

    # Handle missing values based on config
    missing_strategy = config.get("missing_handling", "fill")
    if missing_strategy == "drop":
        df = df.dropna()
    else:
        df = df.fillna(0)

    # Encode all object/string/categorical columns
    for col in df.columns:
        if df[col].dtype == object or str(df[col].dtype).startswith("category"):
            df[col] = LabelEncoder().fit_transform(df[col])

    return df


def _binary_label_dataset_metric(df: pd.DataFrame, config: dict):

    (
        favorable_label,
        unfavorable_label,
        label_name,
        protected_attribute_names,
        privileged_groups,
        unpriviledged_groups,
    ) = _parse_config(config)

    df = preprocess_dataframe(df, config)

    ds = BinaryLabelDataset(
        favorable_label=favorable_label,
        unfavorable_label=unfavorable_label,
        df=df,
        label_names=[label_name],
        protected_attribute_names=protected_attribute_names,
    )
    return BinaryLabelDatasetMetric(
        ds,
        unprivileged_groups=unpriviledged_groups,
        privileged_groups=privileged_groups,
    )


def statistical_parity_difference(df: pd.DataFrame, config: dict) -> float:
    metric = _binary_label_dataset_metric(df, config)
    return metric.statistical_parity_difference()


def num_positives(df: pd.DataFrame, config: dict) -> float:
    metric = _binary_label_dataset_metric(df, config)
    return metric.num_positives()


def num_negatives(df: pd.DataFrame, config: dict) -> float:
    metric = _binary_label_dataset_metric(df, config)
    return metric.num_negatives()


def base_rate(df: pd.DataFrame, config: dict) -> float:
    metric = _binary_label_dataset_metric(df, config)
    return metric.base_rate()


def disparate_impact(df: pd.DataFrame, config: dict) -> float:
    metric = _binary_label_dataset_metric(df, config)
    return metric.disparate_impact()


def consistency(df: pd.DataFrame, config: dict) -> float:
    metric = _binary_label_dataset_metric(df, config)
    return metric.consistency()


def smoothed_empirical_differential_fairness(df: pd.DataFrame, config: dict) -> float:
    metric = _binary_label_dataset_metric(df, config)
    return metric.smoothed_empirical_differential_fairness()


def statistical_parity_difference_wrapper(execution_msg: dict) -> dict:
    return aif360_binary_label_dataset_metric_wrapper(execution_msg, statistical_parity_difference)


def num_positives_wrapper(execution_msg: dict) -> dict:
    return aif360_binary_label_dataset_metric_wrapper(execution_msg, num_positives)


def num_negatives_wrapper(execution_msg: dict) -> dict:
    return aif360_binary_label_dataset_metric_wrapper(execution_msg, num_negatives)


def base_rate_wrapper(execution_msg: dict) -> dict:
    return aif360_binary_label_dataset_metric_wrapper(execution_msg, base_rate)


def disparate_impact_wrapper(execution_msg: dict) -> dict:
    return aif360_binary_label_dataset_metric_wrapper(execution_msg, disparate_impact)


def consistency_wrapper(execution_msg: dict) -> dict:
    return aif360_binary_label_dataset_metric_wrapper(execution_msg, consistency)


def smoothed_empirical_differential_fairness_wrapper(execution_msg: dict) -> dict:
    return aif360_binary_label_dataset_metric_wrapper(execution_msg, smoothed_empirical_differential_fairness)


if __name__ == "__main__":

    artifact_df = dict(location=dict(uri="data/data.csv"))
    artifact_config = dict(location=dict(uri="data/config.json"))

    # All columns in dataframe need to be numerical, NA must not appear
    # csv must contain column names in header
    df = load_dataframe(artifact_df)

    config = load_dict(artifact_config)

    metric = _binary_label_dataset_metric(df, config)

    print(metric.statistical_parity_difference())
    print(metric.num_positives())
    print(metric.num_negatives())
    print(metric.base_rate())
    print(metric.disparate_impact())
    print(metric.consistency())
    print(metric.smoothed_empirical_differential_fairness())
