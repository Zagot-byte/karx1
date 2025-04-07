# smart_result_handler.py
import subprocess
import os
import json
from controller import DeepSeekController # Make sure your controller is wired properly

RESULT_LOG = "deepseek/memory/smart_result_memory.json"

def load_result_memory():
    if os.path.exists(RESULT_LOG):
        with open(RESULT_LOG, "r") as f:
            return json.load(f)
    return {}

def save_result_memory(memory):
    with open(RESULT_LOG, "w") as f:
        json.dump(memory, f, indent=4)

def run_file_and_log(filepath: str):
    result_memory = load_result_memory()
    normalized = os.path.normpath(filepath)
    
    print(f"🚀 Running: {filepath}\n")
    try:
        output = subprocess.check_output(["python", filepath], stderr=subprocess.STDOUT, timeout=10)
        output_text = output.decode("utf-8").strip()

        result_memory[normalized] = {
            "status": "success",
            "output": output_text,
            "attempts": result_memory.get(normalized, {}).get("attempts", 0) + 1,
            "last_fixed": False
        }
        print(f"✅ Execution success:\n{output_text}")

    except subprocess.CalledProcessError as e:
        error_text = e.output.decode("utf-8")
        print(f"❌ Execution failed:\n{error_text}")

        result_memory[normalized] = {
            "status": "error",
            "error": error_text,
            "attempts": result_memory.get(normalized, {}).get("attempts", 0) + 1,
            "last_fixed": False
        }

        # Ask permission before auto-fix
        permission = input("🔧 Want me to fix it automatically? (y/n): ").strip().lower()
        if permission == 'y':
            deepseek = DeepSeekController()
            deepseek.update_file("Fix all bugs and errors.", filepath)
            result_memory[normalized]["last_fixed"] = True
            print("🔁 Retrying after fix...\n")
            return run_file_and_log(filepath)

    save_result_memory(result_memory)

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python smart_result_handler.py <path_to_file>")
    else:
        run_file_and_log(sys.argv[1])
