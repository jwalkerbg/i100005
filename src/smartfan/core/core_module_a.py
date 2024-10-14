# core/core_module_a.py

from smartfan.logger import getAppLogger

logger = getAppLogger(__name__)

def hello_from_core_module_a() -> int:
    logger.info(f"Hello from core_module_a")
    return 1

def goodbye_from_core_module_a() -> int:
    logger.info(f"Goodbye from core_module_a")
    return -1
