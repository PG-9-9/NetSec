import sys
from networksecurity.logging import logger

class NetworkSecurityException(Exception):
    """
    Custom exception class for handling network security-related errors.

    Attributes
    ----------
    error_message : str
        The error message describing the exception.
    lineno : int
        The line number where the exception occurred.
    filename : str
        The name of the file where the exception occurred.

    Methods
    -------
    __str__():
        Returns a formatted string containing the exception details.
    """
    def __init__(self, error_message, error_details:sys): # error_details:sys is a type hint , it comes from the sys module
        """
    Initializes the custom exception with the error message and details.

    Parameters
    ----------
    error_message : str
        The error message describing the exception.
    error_details : sys
        The exception details, including the traceback, from the sys module.
        """
        self.error_message=error_message
        _,_,exc_tb=error_details.exc_info() # exc_info() returns a tuple of three values: the type of the exception, the exception object, and a traceback object

        self.lineno=exc_tb.tb_lineno # tb_lineno is the line number where the exception occurred
        self.filename=exc_tb.tb_frame.f_code.co_filename # Name of the file in which the exception occurred
        
    def __str__(self):
        """
    Returns a formatted string containing the details of the exception, including the file name,
    line number, and the error message.

    Returns
    -------
    str
        A string describing the exception.
        """
        return "Error occured in python file: {0} at line number: {1} with error message: {2}".format(self.filename, self.lineno, self.error_message)
