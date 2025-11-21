import logging
import os
import pickle

from sklearn.linear_model import LogisticRegression
from mki_barebone_io.dict import load_dict, store_dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logreg_model: LogisticRegression

TOOL_WORKDIR = os.getenv("TOOL_WORKDIR", default="")
with open(os.path.join(TOOL_WORKDIR, "data", "model.pkl"), "rb") as fh:
    logreg_model = pickle.load(fh)


def predict_wrapper(execution_msg: dict) -> dict:
    """
    Dispatches the execution message to the predict function of the logistic regression model.

    Args:
    execution_msg (dict): An execution message containing information about the inputs and outputs for the model.
        It should have the following structure:
            - "input": A list of input specifications.
            - "output": A list of output specifications.
            - "func": The name of the function to be executed (not used in this implementation).
            - "meta": Metadata about the execution.

    Returns:
    dict: A dictionary containing the execution message with the output specifications
        updated with the predicted values.
        The output dictionary has the same structure as the input dictionary.
    """

    # input and output specs from execution message
    features_spec = execution_msg["input"][0]
    predictions_spec = execution_msg["output"][0]

    features = load_dict(features_spec)

    predictions = logreg_model.predict(features).tolist()
    logger.debug(f"Computed result {predictions}")

    predictions_spec = store_dict(predictions, predictions_spec)

    # return dict execution message
    return dict(
        func=execution_msg["func"],
        input=execution_msg["input"],
        output=[predictions_spec],
        meta=execution_msg["meta"],
    )
