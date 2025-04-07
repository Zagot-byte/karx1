# deepseek_error_logger.py
import traceback
import json
import os
from datetime import datetime

ERROR_LOG_PATH = "deepseek/memory/deepseek" \
"error_logs.json"

# Ensure error log file exists
if not os.path.exists(ERROR_LOG_PATH):
    with open(ERROR_LOG_PATH, 'w') as f:
        json.dump([], f)

def log_error(file_name, function_name, error, code_context=None):
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "file": file_name,
        "function": function_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "code_context": code_context or ""
    }

    with open(ERROR_LOG_PATH, 'r+') as f:
        logs = json.load(f)
        logs.append(error_entry)
        f.seek(0)
        json.dump(logs, f, indent=4)

def deepseek_try(func):
    """
    Decorator to wrap functions and log any unexpected errors for learning.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            file_name = func.__code__.co_filename
            func_name = func.__name__
            log_error(file_name, func_name, e)
            raise  # Optional: re-raise for user to still see the issue
    return wrapper
