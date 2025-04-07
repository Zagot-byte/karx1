import ast

def parse_file_structure(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        source = file.read()

    tree = ast.parse(source, filename=filepath)

    structure = {
        "classes": [],
        "functions": [],
        "imports": []
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            structure["classes"].append(node.name)
        elif isinstance(node, ast.FunctionDef):
            structure["functions"].append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                structure["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ""
            for alias in node.names:
                structure["imports"].append(f"{module}.{alias.name}")

    return structure
