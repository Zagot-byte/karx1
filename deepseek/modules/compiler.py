# deepseek/compiler.py

import os
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MEMORY_PATH = PROJECT_ROOT / "deepseek" / "memory" / "code_memory.json"
SCAN_ROOT = PROJECT_ROOT  # You can change this to a subfolder if needed

def extract_structure_from_code(code):
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

def scan_directory_and_update_memory():
    memory = {}
    for root, dirs, files in os.walk(SCAN_ROOT):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        code = f.read()
                    rel_path = os.path.relpath(filepath, PROJECT_ROOT)
                    classes, functions, imports = extract_structure_from_code(code)
                    memory[rel_path] = {
                        "classes": classes,
                        "functions": functions,
                        "imports": imports
                    }
                except Exception as e:
                    print(f"⚠️ Could not read {filepath}: {e}")

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)
    
    print(f"✅ Memory rebuilt successfully with {len(memory)} files.")

if __name__ == "__main__":
    scan_directory_and_update_memory()
