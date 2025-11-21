"""A generated script for importing and calling tool functions"""

from scikit_metrics.metric_server import accuracy_wrapper
from scikit_metrics.metric_server import precision_wrapper
from scikit_metrics.metric_server import recall_wrapper
from scikit_metrics.metric_server import f1_wrapper
from scikit_metrics.metric_server import roc_auc_wrapper
from scikit_metrics.metric_server import mcc_wrapper
from scikit_metrics.metric_server import mse_wrapper
from scikit_metrics.metric_server import specificity_wrapper
from scikit_metrics.metric_server import balanced_accuracy_wrapper
from scikit_metrics.metric_server import tp_wrapper
from scikit_metrics.metric_server import fp_wrapper
from scikit_metrics.metric_server import tn_wrapper
from scikit_metrics.metric_server import fn_wrapper



def funcwrapper(exec_message: dict):
    """A wrapper for tool functions

    Args:
        exec_message (dict): The execution message that contains the function name, input and output specs.

    Raises:
        Exception: If trying to call a function that the tool does not provide.
    """
    funcname = exec_message["func"]

    if funcname == "accuracy_wrapper":
        return accuracy_wrapper(exec_message)
    if funcname == "precision_wrapper":
        return precision_wrapper(exec_message)
    if funcname == "recall_wrapper":
        return recall_wrapper(exec_message)
    if funcname == "f1_wrapper":
        return f1_wrapper(exec_message)
    if funcname == "roc_auc_wrapper":
        return roc_auc_wrapper(exec_message)
    if funcname == "mcc_wrapper":
        return mcc_wrapper(exec_message)
    if funcname == "mse_wrapper":
        return mse_wrapper(exec_message)
    if funcname == "specificity_wrapper":
        return specificity_wrapper(exec_message)
    if funcname == "balanced_accuracy_wrapper":
        return balanced_accuracy_wrapper(exec_message)
    if funcname == "tp_wrapper":
        return tp_wrapper(exec_message)
    if funcname == "fp_wrapper":
        return fp_wrapper(exec_message)
    if funcname == "tn_wrapper":
        return tn_wrapper(exec_message)
    if funcname == "fn_wrapper":
        return fn_wrapper(exec_message)
    
    raise Exception(f"Function {funcname} not found")