import os
import time
from pathlib import Path
import tkinter as tk

OUTPUT_FILE = "../memory/deepseek_output.txt"
OFFLINE_MODE = True  # Set False to allow Git push

def get_clipboard_text():
    root = tk.Tk()
    root.withdraw()  # Hide the GUI window
    try:
        text = root.clipboard_get()
    except tk.TclError:
        text = ""
    root.destroy()
    return text

def monitor_clipboard():
    last_text = ""
    print("🧠 Clipboard monitoring started (no pyperclip). Copy any LLM output to auto-save it!")

    while True:
        try:
            text = get_clipboard_text()
            if text != last_text and text.strip():
                last_text = text
                print("📎 New clipboard content detected. Saving to output file...")
                save_output(text)
            time.sleep(1)
        except KeyboardInterrupt:
            print("👋 Exiting clipboard monitor.")
            break

def save_output(text):
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"💾 Saved output to {OUTPUT_FILE}")
    print("📣 Ready for DeepSeek Writer & Teacher to pick it up!")

if __name__ == "__main__":
    print("🚀 Launching Clipboard Listener...")
    monitor_clipboard()
