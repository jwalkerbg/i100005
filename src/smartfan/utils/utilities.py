# utils/utilities.py

from smartfan.logger import getAppLogger

logger = getAppLogger(__name__)

def hello_from_utils() ->  None:
    logger.info(f"Hello from utils")

# this function is used to demostrate unittest and pytest styles of unit testing
def sumator(a:int, b:int, c:int) -> int:
    return a + b + c