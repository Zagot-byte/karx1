import os
import shutil
from pathlib import Path
import json

MEMORY_PATH = Path("deepseek/memory/code_memory.json")

class FileManager:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir).resolve()
        self.memory = self.load_memory()

    def load_memory(self):
        if not MEMORY_PATH.exists():
            return {}
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_memory(self):
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4)

    def list_files(self):
        print("📁 Project files:")
        for path in self.base_dir.rglob("*"):
            if path.is_file():
                print(" -", path.relative_to(self.base_dir))

    def delete(self, rel_path):
        full_path = self.base_dir / rel_path
        if not full_path.exists():
            print(f"❌ File not found: {rel_path}")
            return

        if full_path.is_dir():
            shutil.rmtree(full_path)
            print(f"🗑️ Folder deleted: {rel_path}")
        else:
            full_path.unlink()
            print(f"🗑️ File deleted: {rel_path}")

        norm = os.path.normpath(str(full_path))
        if norm in self.memory:
            del self.memory[norm]
            self.save_memory()

    def rename(self, old_rel_path, new_rel_path):
        old_path = self.base_dir / old_rel_path
        new_path = self.base_dir / new_rel_path
        new_path.parent.mkdir(parents=True, exist_ok=True)

        if not old_path.exists():
            print(f"❌ Path not found: {old_rel_path}")
            return

        shutil.move(str(old_path), str(new_path))
        print(f"✏️ Renamed: {old_rel_path} → {new_rel_path}")

        old_norm = os.path.normpath(str(old_path))
        new_norm = os.path.normpath(str(new_path))

        if old_norm in self.memory:
            self.memory[new_norm] = self.memory.pop(old_norm)
            self.save_memory()

    def move_file(self, src_rel, dest_rel):
        self.rename(src_rel, dest_rel)


# For quick testing
if __name__ == "__main__":
    fm = FileManager()
    fm.list_files()

    # Uncomment these for testing:
    # fm.rename("deepseek/sample.py", "deepseek/modules/sample_module.py")
    # fm.delete("deepseek/old_code/legacy_utils.py")
    # fm.move_file("deepseek/temp/code1.py", "deepseek/core/code1.py")
