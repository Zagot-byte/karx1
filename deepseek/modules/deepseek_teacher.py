import os
import json
import requests

def load_memory(memory_path="deepseek/memory/code_memory.json"):
    """
    Loads the memory index that contains information about files,
    their classes, functions, and imports.
    """
    if not os.path.exists(memory_path):
        return {}
    with open(memory_path, "r") as f:
        return json.load(f)

def read_code_file(filepath):
    """
    Reads the contents of a code file and returns it as a string.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def build_prompt(filepath, memory):
    """
    Builds a prompt using file content and memory information
    to query the DeepSeek model with full context.
    """
    filename = os.path.normpath(filepath)
    file_info = memory.get(filename, {})

    code = read_code_file(filepath)

    system_context = f"""You are an expert programming teacher.
You will explain the following Python code to a beginner-level student with clear, human-friendly language.

Explain:
- The purpose of the file.
- The role of each class and function.
- The libraries used and why.
- Any relationships with other files, if known.

File: {filename}
Imports: {file_info.get('imports', [])}
Classes: {file_info.get('classes', [])}
Functions: {file_info.get('functions', [])}

Now explain the code:
-----------------------------
{code}
-----------------------------
"""
    return system_context

def query_deepseek(prompt, model="deepseek-coder"):
    """
    Sends the prompt to your local DeepSeek model running via Ollama
    and streams the explanation response back.
    """
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt},
        stream=True
    )

    explanation = ""
    for line in response.iter_lines():
        if line:
            explanation += line.decode("utf-8")
    return explanation

def explain(filepath):
    """
    Main function to use: given a Python file path, it loads memory,
    builds a prompt, and returns DeepSeek's explanation.
    """
    memory = load_memory()
    prompt = build_prompt(filepath, memory)
    explanation = query_deepseek(prompt)
    return explanation

# Example test run
if __name__ == "__main__":
    target_file = "deepseek/executing and teaching/deepseek_runner.py"  # Change this path as needed
    print("🔍 Explaining:", target_file)
    result = explain(target_file)
    print("\n🧠 Code Explanation:\n")
    print(result)
