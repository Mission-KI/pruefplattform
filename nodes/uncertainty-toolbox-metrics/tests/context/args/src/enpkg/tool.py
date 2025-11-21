"""A generated script for importing and calling tool functions"""

from uct_wrapper.impl import mean_absolute_calibration_error
from uct_wrapper.impl import expected_calibration_error
from uct_wrapper.impl import root_mean_squared_calibration_error
from uct_wrapper.impl import miscalibration_area
from uct_wrapper.impl import interval_score
from uct_wrapper.impl import check_score
from uct_wrapper.impl import negative_log_likelihood
from uct_wrapper.impl import continuous_ranked_probability_score
from uct_wrapper.impl import expected_standard_deviation



def funcwrapper(exec_message: dict):
    """A wrapper for tool functions

    Args:
        exec_message (dict): The execution message that contains the function name, input and output specs.

    Raises:
        Exception: If trying to call a function that the tool does not provide.
    """
    funcname = exec_message["func"]

    if funcname == "mean_absolute_calibration_error":
        return mean_absolute_calibration_error(exec_message)
    if funcname == "expected_calibration_error":
        return expected_calibration_error(exec_message)
    if funcname == "root_mean_squared_calibration_error":
        return root_mean_squared_calibration_error(exec_message)
    if funcname == "miscalibration_area":
        return miscalibration_area(exec_message)
    if funcname == "interval_score":
        return interval_score(exec_message)
    if funcname == "check_score":
        return check_score(exec_message)
    if funcname == "negative_log_likelihood":
        return negative_log_likelihood(exec_message)
    if funcname == "continuous_ranked_probability_score":
        return continuous_ranked_probability_score(exec_message)
    if funcname == "expected_standard_deviation":
        return expected_standard_deviation(exec_message)
    
    raise Exception(f"Function {funcname} not found")