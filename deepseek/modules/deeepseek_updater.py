from pathlib import Path

PROMPT_FILE = "../Prompts/new_idea.txt"
MEMORY_FILE = "../memory/deepseek_output.txt"
import os
import json
import requests

def update_file_with_deepseek(update_prompt, filepath, memory_path="deepseek/memory/code_memory.json"):
    """
    Updates an existing Python file using DeepSeek based on a new prompt.
    Only the relevant parts of the code should change.
    """

    def load_memory():
        if not os.path.exists(memory_path):
            return {}
        with open(memory_path, "r") as f:
            return json.load(f)

    def save_memory(memory):
        with open(memory_path, "w") as f:
            json.dump(memory, f, indent=4)

    def extract_structure(code):
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

    def build_update_prompt(update_prompt, memory, existing_code):
        memory_summary = json.dumps(memory, indent=2)
        return f"""You are an expert code editor AI.

You will receive an existing Python file and a task.
Your job is to update the file according to the instruction.

Instruction:
"{update_prompt}"

ONLY modify what's necessary. Do not rewrite the whole code unless absolutely needed.

Existing code:
{existing_code}

Current memory:
{memory_summary}
"""

    def query_deepseek(prompt, model="deepseek-coder"):
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": True}
        )
        code = ""
        for line in response.iter_lines():
            if line:
                code += line.decode("utf-8")
        return code

    def read_file(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def write_file(code, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        return extract_structure(code)

    # Begin updating...
    memory = load_memory()
    existing_code = read_file(filepath)
    prompt = build_update_prompt(update_prompt, memory, existing_code)
    updated_code = query_deepseek(prompt)

    classes, functions, imports = write_file(updated_code, filepath)

    # Update memory
    normalized_path = os.path.normpath(filepath)
    memory[normalized_path] = {
        "classes": classes,
        "functions": functions,
        "imports": imports
    }
    save_memory(memory)

    print(f"🔁 File updated: {filepath}")
    print(f"🧠 Memory refreshed with → Classes: {classes}, Functions: {functions}")


def read_prompt_file():
    prompt_path = Path(PROMPT_FILE)
    if not prompt_path.exists():
        print("📭 No prompt file found.")
        return None

    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print("📭 Prompt file is empty.")
        return None

    return content

def update_memory_with_prompt(prompt):
    memory_path = Path(MEMORY_FILE)
    memory_path.parent.mkdir(parents=True, exist_ok=True)

    if memory_path.exists():
        with open(memory_path, "r", encoding="utf-8") as f:
            current_memory = f.read()
    else:
        current_memory = ""

    if prompt in current_memory:
        print("⚠️ Prompt already exists in memory. Skipping.")
        return

    with open(memory_path, "a", encoding="utf-8") as f:
        f.write("\n\n# 🧠 New Idea\n")
        f.write(prompt)

    print("✅ Memory successfully updated with new idea!")

def main():
    print("🔄 Checking for new prompt to update memory...")
    prompt = read_prompt_file()
    if prompt:
        update_memory_with_prompt(prompt)

if __name__ == "__main__":
    print("📘 DeepSeek Updater is running...")
    main()
