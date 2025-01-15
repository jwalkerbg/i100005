# utils/utilities.py

from smartfan.logger import get_app_logger

logger = get_app_logger(__name__)

def hello_from_utils() ->  None:
    logger.info("Hello from utils")
