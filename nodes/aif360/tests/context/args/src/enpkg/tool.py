"""A generated script for importing and calling tool functions"""

from aif360_wrapper.wrapper import statistical_parity_difference_wrapper
from aif360_wrapper.wrapper import num_positives_wrapper
from aif360_wrapper.wrapper import num_negatives_wrapper
from aif360_wrapper.wrapper import base_rate_wrapper
from aif360_wrapper.wrapper import disparate_impact_wrapper
from aif360_wrapper.wrapper import consistency_wrapper
from aif360_wrapper.wrapper import smoothed_empirical_differential_fairness_wrapper



def funcwrapper(exec_message: dict):
    """A wrapper for tool functions

    Args:
        exec_message (dict): The execution message that contains the function name, input and output specs.

    Raises:
        Exception: If trying to call a function that the tool does not provide.
    """
    funcname = exec_message["func"]

    if funcname == "statistical_parity_difference_wrapper":
        return statistical_parity_difference_wrapper(exec_message)
    if funcname == "num_positives_wrapper":
        return num_positives_wrapper(exec_message)
    if funcname == "num_negatives_wrapper":
        return num_negatives_wrapper(exec_message)
    if funcname == "base_rate_wrapper":
        return base_rate_wrapper(exec_message)
    if funcname == "disparate_impact_wrapper":
        return disparate_impact_wrapper(exec_message)
    if funcname == "consistency_wrapper":
        return consistency_wrapper(exec_message)
    if funcname == "smoothed_empirical_differential_fairness_wrapper":
        return smoothed_empirical_differential_fairness_wrapper(exec_message)
    
    raise Exception(f"Function {funcname} not found")