# drivers/ina236.py

from pymodule.logger import getAppLogger

logger = getAppLogger(__name__)

def hello_from_ina236() -> None:
    logger.info(f"Hello from ina236")