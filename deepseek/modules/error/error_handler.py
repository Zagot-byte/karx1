# File: error_handler.py

import os
import json
import requests
import traceback
import runpy

def run_and_log(filepath, error_log_path="deepseek/errors/error_logs.json"):
    try:
        runpy.run_path(filepath, run_name="__main__")
        print("✅ No error while running:", filepath)
    except Exception as e:
        error_entry = {
            "filepath": filepath,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

        # Save the error
        if os.path.exists(error_log_path):
            with open(error_log_path, "r") as f:
                errors = json.load(f)
        else:
            errors = {}

        errors[filepath] = error_entry
        os.makedirs(os.path.dirname(error_log_path), exist_ok=True)
        with open(error_log_path, "w") as f:
            json.dump(errors, f, indent=2)

        print(f"❌ Error captured and logged for: {filepath}")
        print("🧠 Waiting for your permission to auto-fix...")

def smart_fix(filepath, memory_path="deepseek/memory/code_memory.json", error_log_path="deepseek/errors/error_logs.json"):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    if not os.path.exists(error_log_path):
        print(f"❌ No error logs found at {error_log_path}")
        return

    # Load the last error for this file
    with open(error_log_path, "r") as f:
        all_errors = json.load(f)
    error_entry = all_errors.get(filepath)
    if not error_entry:
        print(f"⚠️ No recorded errors for {filepath}")
        return

    error_traceback = error_entry.get("traceback", "")
    error_message = error_entry.get("error", "")

    # Load the original code
    with open(filepath, "r", encoding="utf-8") as f:
        original_code = f.read()

    # Load memory
    memory = {}
    if os.path.exists(memory_path):
        with open(memory_path, "r") as f:
            memory = json.load(f)

    # Build the prompt
    prompt = f"""
You are a professional AI code debugger.

Fix the following Python file based on the traceback error below:

--- ORIGINAL CODE ---
{original_code}

--- ERROR TRACEBACK ---
{error_traceback}

--- ERROR MESSAGE ---
{error_message}

--- MEMORY (for context) ---
{json.dumps(memory, indent=2)}

Return the complete updated code ONLY.
"""

    # Ask DeepSeek to
