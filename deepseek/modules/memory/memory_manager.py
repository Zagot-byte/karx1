import os
import json

MEMORY_FILE = "code_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory_data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, indent=4)

def update_memory(file_path, new_structure):
    memory = load_memory()
    memory[file_path] = new_structure
    save_memory(memory)

def get_file_structure(file_path):
    memory = load_memory()
    return memory.get(file_path, {})

def list_all_files():
    memory = load_memory()
    return list(memory.keys())

def list_all_classes():
    memory = load_memory()
    return {
        file: data.get("classes", [])
        for file, data in memory.items()
    }

def list_all_functions():
    memory = load_memory()
    return {
        file: data.get("functions", [])
        for file, data in memory.items()
    }
