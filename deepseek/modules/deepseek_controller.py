import os
import json
import requests
import time
from pathlib import Path
import sys
import os

from error import error_handler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def handle_update_prompt_from_file(self, update_txt_path):
    """
    Handles a .txt file from Updates/ containing file path and instruction.
    Format:
    File: deepseek/generated/somefile.py

    Update:
    Add logging to all functions.
    """
    if not os.path.exists(update_txt_path):
        print(f"❌ Update prompt file not found: {update_txt_path}")
        return

    with open(update_txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "File:" not in content or "Update:" not in content:
        print("❌ Invalid format. Must contain 'File:' and 'Update:'")
        return

    try:
        filepath = content.split("File:")[1].split("Update:")[0].strip()
        update_instruction = content.split("Update:")[1].strip()

        print(f"🔄 Processing update:\n📄 File: {filepath}\n📝 Instruction: {update_instruction}")
        self.update_file(update_instruction, filepath)
    except Exception as e:
        print(f"❌ Error processing update prompt: {e}")
def fix_errors(self, filepath): 
    error_handler.smart_fix(filepath)
    # Add this in your DeepSeekController class

def run_with_smart_fix(self, filepath):
    error_handler.run_and_log(filepath)
    prompt_user_to_fix(filepath) # type: ignore


class DeepSeekController:
    def __init__(self, memory_path="deepseek/memory/code_memory.json"):
        self.memory_path = memory_path
        self.memory = self.load_memory()

    def load_memory(self):
        if not os.path.exists(self.memory_path):
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            return {}
        with open(self.memory_path, "r") as f:
            return json.load(f)

    def save_memory(self):
        with open(self.memory_path, "w") as f:
            json.dump(self.memory, f, indent=4)

    def extract_structure(self, code):
        classes, functions, imports = [], [], []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith("class "):
                classes.append(stripped.split()[1].split("(")[0])
            elif stripped.startswith("def "):
                functions.append(stripped.split()[1].split("(")[0])
            elif stripped.startswith("import ") or stripped.startswith("from "):
                imports.append(stripped)
        return classes, functions, imports

    def query_deepseek(self, prompt, model="deepseek-coder"):
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": True}
        )
        code = ""
        for line in response.iter_lines():
            if line:
                code += json.loads(line.decode("utf-8"))["response"]
        return code

    def build_writer_prompt(self, user_prompt):
        memory_summary = json.dumps(self.memory, indent=2)
        return f"""You are a helpful AI developer assistant.

You need to generate a Python file based on the following user instruction:

"{user_prompt}"

Guidelines:
- Write clean, modular Python code.
- Follow Python best practices.
- Use existing memory context where useful.
- Output only code. No explanation.

Memory summary:
{memory_summary}
"""

    def write_code_file(self, code, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code.strip())
        return self.extract_structure(code)

    def generate_file(self, user_prompt, filepath):
        prompt = self.build_writer_prompt(user_prompt)
        code = self.query_deepseek(prompt)
        classes, functions, imports = self.write_code_file(code, filepath)

        normalized_path = os.path.normpath(filepath)
        self.memory[normalized_path] = {
            "classes": classes,
            "functions": functions,
            "imports": imports
        }
        self.save_memory()
        print(f"✅ File generated: {filepath}")
        print(f"🧠 Memory updated with → Classes: {classes}, Functions: {functions}")

    def watch_prompt_folder(self, prompt_folder="Prompts", output_folder="deepseek/generated", poll_interval=3):
        prompt_dir = Path(prompt_folder)
        processed_dir = prompt_dir / "processed"
        os.makedirs(processed_dir, exist_ok=True)

        print("👀 Watching prompt folder... Drop `.txt` files into 'Prompts/'")

        while True:
            for file in prompt_dir.glob("*.txt"):
                with open(file, "r", encoding="utf-8") as f:
                    prompt = f.read().strip()

                filename = f"{file.stem}.py"
                filepath = os.path.join(output_folder, filename)
                self.generate_file(prompt, filepath)

                file.rename(processed_dir / file.name)
            time.sleep(poll_interval)
