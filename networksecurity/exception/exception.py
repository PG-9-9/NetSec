import sys
from networksecurity.logging import logger

class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_details:sys): # error_details:sys is a type hint , it comes from the sys module
        self.error_message=error_message
        _,_,exc_tb=error_details.exc_info() # exc_info() returns a tuple of three values: the type of the exception, the exception object, and a traceback object

        self.lineno=exc_tb.tb_lineno # tb_lineno is the line number where the exception occurred
        self.filename=exc_tb.tb_frame.f_code.co_filename # Name of the file in which the exception occurred
        
    def __str__(self):
        return "Error occured in python file: {0} at line number: {1} with error message: {2}".format(self.filename, self.lineno, self.error_message)

# if __name__=="__main__":
#     try:
#         logger.logging.info("This is a test message")
#         a=10/0
#         print("This will not be printed",a)
#     except Exception as e:
#             raise NetworkSecurityException(e, sys) # sys is passed as the error_details argument