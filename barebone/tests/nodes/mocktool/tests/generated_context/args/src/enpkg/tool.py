"""A generated script for importing and calling tool functions"""

from toolpkg.metric import fourtyone_wrapper
from toolpkg.metric import fourtytwo_wrapper



def funcwrapper(exec_message: dict):
    """A wrapper for tool functions

    Args:
        exec_message (dict): The execution message that contains the function name, input and output specs.

    Raises:
        Exception: If trying to call a function that the tool does not provide.
    """
    funcname = exec_message["func"]

    if funcname == "fourtyone_wrapper":
        return fourtyone_wrapper(exec_message)
    if funcname == "fourtytwo_wrapper":
        return fourtytwo_wrapper(exec_message)
    
    raise Exception(f"Function {funcname} not found")