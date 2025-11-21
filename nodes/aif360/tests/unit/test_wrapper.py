from aif360_wrapper.wrapper import _binary_label_dataset_metric
from mki_barebone_io.dict import load_dict, store_dict
from mki_barebone_io.dataframe import load_dataframe

import pytest
import os


@pytest.mark.unit
@pytest.mark.aif360
def test_wrapper(node_test_dir):

    artifact_df = dict(location=dict(uri=os.path.join(node_test_dir, "data", "data.csv")))
    artifact_config = dict(location=dict(uri=os.path.join(node_test_dir, "data", "config.json")))

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
