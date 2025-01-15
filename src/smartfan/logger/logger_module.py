# logger.py

# logger_module.py
from typing import List
import logging
from datetime import datetime

TAGNAME = "smartfan"

# Custom Formatter
class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{log_time} - {record.name} - {record.levelname} - {record.getMessage()}"
        return log_message

# Custom Logging Handler
class StringHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_messages = []

    def emit(self, record):
        log_entry = self.format(record)
        self.log_messages.append(log_entry)

    def get_logs(self):
        return '\n'.join(self.log_messages)

    def clear_logs(self):
        self.log_messages = []

# Create the custom formatter and string handler
custom_formatter = CustomFormatter()
console_handler = logging.StreamHandler()
console_handler.setFormatter(custom_formatter)
string_handler = StringHandler()
string_handler.setFormatter(custom_formatter)

def get_app_logger(area_tag:str, to_string:bool=False) -> logging.Logger:
    if not area_tag or len(area_tag) == 0:
        return None
    lg = logging.getLogger(area_tag)
    lg.setLevel(logging.INFO)
    lg.addHandler(console_handler)
    if to_string:
        lg.addHandler(string_handler)

    return lg

def add_string_handler(lg:logging.Logger) -> None:
    lg.addHandler(string_handler)

def disable_string_handler() -> None:
    string_handler.addFilter(lambda record: False)

def enable_string_handler() -> None:
    string_handler.filters.clear()

def get_string_logs() -> List[str]:
    return string_handler.get_logs()

def clear_string_logs() -> None:
    string_handler.clear_logs()
