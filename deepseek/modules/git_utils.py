# git_utils.py

import subprocess
from datetime import datetime

OFFLINE_MODE = False  # Set this to True if you want to disable Git sync temporarily

def manual_git_push(commit_message="Manual push from DeepSeek"):
    """
    🌐 Manually push all staged changes to Git.
    Includes timestamp and handles errors.
    """
    if OFFLINE_MODE:
        print("📴 Offline mode is enabled. Skipping Git push.")
        return

    try:
        print("📦 Staging all changes...")
        subprocess.run(["git", "add", "."], check=True)

        full_message = f"{commit_message} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"📝 Committing: {full_message}")
        subprocess.run(["git", "commit", "-m", full_message], check=True)

        print("🚀 Pushing to remote...")
        subprocess.run(["git", "push"], check=True)

        print("✅ Git push completed successfully!")

    except subprocess.CalledProcessError as e:
        print("❌ Git push failed:", e)
