import os
import ast
import json

class MemoryBuilder:
    def __init__(self, base_path="deepseek", memory_path="deepseek/memory/code_memory.json"):
        self.base_path = base_path
        self.memory_path = memory_path
        self.memory = {}

    def build(self):
        for root, _, files in os.walk(self.base_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    self.memory[full_path] = self._analyze_file(full_path)

        self._save_memory()

    def _analyze_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return {"error": "Syntax error in file"}

        functions = []
        classes = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                imports.append(module)

        return {
            "functions": functions,
            "classes": classes,
            "imports": list(set(imports))  # remove duplicates
        }

    def _save_memory(self):
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2)

# Optional test run
if __name__ == "__main__":
    builder = MemoryBuilder()
    builder.build()
    print("Memory has been built and saved.")
