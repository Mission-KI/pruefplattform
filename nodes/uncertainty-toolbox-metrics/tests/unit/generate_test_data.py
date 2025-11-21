import os
from typing import List, Dict

import numpy as np
import pyarrow as pa

from mki_barebone_io.arrow import store_arrow, load_arrow

schemas = {
    "predictions": pa.schema(
        [
            pa.field("prediction_mean", pa.float64(), nullable=False),
            pa.field("prediction_std", pa.float64(), nullable=False),
        ]
    ),
    "standard_deviations": pa.schema(
        [
            pa.field("prediction_std", pa.float64(), nullable=False),
        ]
    ),
    "labels": pa.schema(
        [
            pa.field("label", pa.float64(), nullable=False),
        ]
    ),
}


def generate_batch_of_tables(n_rows: int, n_batches, seed: int) -> Dict[str, List[pa.Table]]:

    # Set the random seed for reproducibility
    np.random.seed(seed)

    # Define a real-valued function that a hypothetical model was tasked to fit
    def func(x):
        return x**2 + 2 * x + 1

    prediction_batches = []
    label_batches = []
    std_batches = []
    for b in range(n_batches):
        # Generate the x values
        x_values = np.linspace(-10, 10, n_rows)

        # Calculate the function values
        labels = func(x_values)

        # Add random noise to the function values
        prediction_means = labels + np.random.normal(0, 1, n_rows)

        # Generate samples from a normal Gaussian distribution
        prediction_stds = np.abs(np.random.normal(0, 1, n_rows))

        label_batches.append(pa.table({"label": labels}, schema=schemas["labels"]))
        prediction_batches.append(
            pa.table(
                {"prediction_mean": prediction_means, "prediction_std": prediction_stds}, schema=schemas["predictions"]
            )
        )
        std_batches.append(pa.table({"prediction_std": prediction_stds}, schema=schemas["standard_deviations"]))

    return dict(predictions=prediction_batches, labels=label_batches, standard_deviations=std_batches)


if __name__ == "__main__":
    # Generate test data
    batches = generate_batch_of_tables(n_rows=16, n_batches=2, seed=42)
    data_folder = os.path.join("tests", "data")

    # write data to files
    for data_type in ["predictions", "labels", "standard_deviations"]:
        store_arrow(
            batches[data_type],
            dict(location={"uri": os.path.join(data_folder, f"{data_type}.arrow")}),
            schemas[data_type],
        )

    # # read data from files
    # read_batches = {}
    # for data_type in ["predictions", "labels", "standard_deviations"]:
    #     read_batches[data_type] = load_arrow(
    #         dict(location={"uri": os.path.join(data_folder, f"{data_type}.arrow")}),
    #         schemas[data_type],
    #     )
