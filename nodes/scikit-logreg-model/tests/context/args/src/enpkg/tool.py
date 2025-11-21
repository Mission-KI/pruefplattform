"""A generated script for importing and calling tool functions"""

from logreg_model_wrapper.impl import predict_wrapper



def funcwrapper(exec_message: dict):
    """A wrapper for tool functions

    Args:
        exec_message (dict): The execution message that contains the function name, input and output specs.

    Raises:
        Exception: If trying to call a function that the tool does not provide.
    """
    funcname = exec_message["func"]

    if funcname == "predict_wrapper":
        return predict_wrapper(exec_message)
    
    raise Exception(f"Function {funcname} not found")