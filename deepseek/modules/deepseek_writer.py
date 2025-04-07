import os
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from deepseek_teacher import explain_code_like_teacher

OFFLINE_MODE = True
MEMORY_JSON = "deepseek/memory/code_memory.json"
OUTPUT_TXT = "memory/deepseek_output.txt"
PROJECT_ROOT = Path(__file__).parent.parent
ROOT_FOLDER = PROJECT_ROOT

class GitSyncManager:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path

    def sync_changes(self, commit_message="Auto-sync from DeepSeek"):
        if OFFLINE_MODE:
            print("🌐 Offline mode. Git sync skipped.")
            return
        try:
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
            full_msg = f"{commit_message} - {datetime.now()}"
            subprocess.run(["git", "commit", "-m", full_msg], cwd=self.repo_path, check=True)
            subprocess.run(["git", "push"], cwd=self.repo_path, check=True)
            print("✅ Git sync complete.")
        except subprocess.CalledProcessError as e:
            print("⚠️ Git sync failed:", e)

class DeepSeekWriter:
    def __init__(self):
        self.memory_path = MEMORY_JSON

    def _load_memory(self):
        if not os.path.exists(self.memory_path):
            return {}
        with open(self.memory_path, "r") as f:
            return json.load(f)

    def _save_memory(self, memory):
        with open(self.memory_path, "w") as f:
            json.dump(memory, f, indent=2)

    def _extract_structure(self, code):
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

    def _query_deepseek(self, prompt, model="deepseek-coder"):
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": True}
        )
        code = ""
        for line in response.iter_lines():
            if line:
                code += line.decode("utf-8")
        return code

    def _write_file(self, code, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        return self._extract_structure(code)

    def _build_prompt(self, user_prompt, memory):
        memory_summary = json.dumps(memory, indent=2)
        return f"""You are an expert developer AI.

Your job is to generate a new Python file based on this instruction:
"{user_prompt}"

You must:
- Write clean, modular Python code.
- Use existing structure when useful.
- Only return code. No explanation.

Current memory:
{memory_summary}
"""

    def generate_file_with_prompt(self, user_prompt, filepath):
        memory = self._load_memory()
        prompt = self._build_prompt(user_prompt, memory)
        code = self._query_deepseek(prompt)
        classes, functions, imports = self._write_file(code, filepath)

        memory[os.path.normpath(filepath)] = {
            "classes": classes,
            "functions": functions,
            "imports": imports
        }
        self._save_memory(memory)

        explain_code_like_teacher(filepath, code)
        self._check_and_fix_errors(filepath)

        print(f"✅ Generated: {filepath}")
        print(f"📚 Memory updated with → Classes: {classes}, Functions: {functions}")

    def _check_and_fix_errors(self, file_path):
        ext = Path(file_path).suffix
        if ext == ".py":
            subprocess.run(["pylint", file_path])
            subprocess.run(["autopep8", "--in-place", "--aggressive", file_path])
        elif ext in [".js", ".ts"]:
            subprocess.run(["eslint", file_path, "--fix"])
        elif ext == ".dart":
            subprocess.run(["dart", "analyze", file_path])
        else:
            print(f"⚠️ No linter setup for {ext}")

    def execute_batch_from_memory(self, memory_txt_path=OUTPUT_TXT):
        path = Path(memory_txt_path)
        if not path.exists():
            print("❌ No memory instruction file found.")
            return

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        instructions = self._extract_batch_instructions(text)
        self._write_batch_files(instructions)

        GitSyncManager().sync_changes("Auto-batch write from DeepSeek")

    def _extract_batch_instructions(self, text):
        instructions = []
        lines = text.splitlines()
        current_file = None
        current_content = []

        for line in lines:
            if line.startswith("Create a file:"):
                if current_file:
                    instructions.append((current_file, "\n".join(current_content)))
                    current_content = []
                current_file = line.split(":", 1)[1].strip()
            elif current_file:
                current_content.append(line)

        if current_file:
            instructions.append((current_file, "\n".join(current_content)))

        return instructions

    def _write_batch_files(self, instructions):
        for rel_path, content in instructions:
            full_path = ROOT_FOLDER / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write("# 🧠 Auto-generated by DeepSeek\n")
                f.write(content.strip() + "\n")

            print(f"✅ Created: {rel_path}")

# Example Usage
if __name__ == "__main__":
    writer = DeepSeekWriter()
    
    # Option 1: Prompt-based single file generation
    # writer.generate_file_with_prompt("Create a utility for merging PDFs", "tools/pdf_merger.py")

    # Option 2: Execute from batch memory dump
    writer.execute_batch_from_memory()

