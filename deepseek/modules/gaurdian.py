import os
import time
import subprocess
import psutil
import logging
import psutil
import GPUtil
import logging
from datetime import datetime

class GuardianAngel:
    def __init__(self,
                 cpu_threshold: int = 85,
                 ram_threshold: int = 85,
                 vram_threshold: int = 90,
                 log_file: str = "guardian_logs.log"):
        self.cpu_threshold = cpu_threshold
        self.ram_threshold = ram_threshold
        self.vram_threshold = vram_threshold
        self.log_file = log_file
        self._setup_logger()

    def _setup_logger(self):
        logging.basicConfig(
            filename=self.log_file,
            filemode='a',
            format='%(asctime)s | %(levelname)s | %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger("GuardianAngel")

    def get_system_stats(self) -> dict:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent

        try:
            gpus = GPUtil.getGPUs()
            vram_usage = max([gpu.memoryUtil * 100 for gpu in gpus]) if gpus else 0
        except Exception as e:
            self.logger.warning(f"Unable to access GPU info: {e}")
            vram_usage = 0

        return {
            "cpu": round(cpu_usage, 2),
            "ram": round(ram_usage, 2),
            "vram": round(vram_usage, 2)
        }

    def is_safe_to_proceed(self) -> bool:
        stats = self.get_system_stats()
        status = all([
            stats["cpu"] < self.cpu_threshold,
            stats["ram"] < self.ram_threshold,
            stats["vram"] < self.vram_threshold
        ])

        self._log_decision(stats, status)
        return status

    def _log_decision(self, stats: dict, status: bool):
        message = (f"System Status | CPU: {stats['cpu']}%, "
                   f"RAM: {stats['ram']}%, VRAM: {stats['vram']}%")

        if status:
            self.logger.info(f"[SAFE] {message}")
        else:
            self.logger.warning(f"[UNSAFE] {message} — Operation Blocked")

    def warn_user(self):
        print("\n⚠️  System load is too high for safe AI operations.")
        print("🧠 CPU: {}% | 🗂 RAM: {}% | 🎮 VRAM: {}%".format(*self.get_system_stats().values()))
        print("🛑 Operation halted to protect your machine.\n")


# Safe Mode Toggle
SAFE_MODE = True

# Resource Thresholds
MAX_CPU = 85  # in percent
MAX_RAM = 85  # in percent
MAX_RUNTIME = 15  # seconds per file run

# Logging Setup
LOG_DIR = "deepseek/safety/logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "system_monitor.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def check_resources():
    """Returns True if system usage is safe."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    
    if cpu > MAX_CPU or ram > MAX_RAM:
        logging.warning(f"High usage — CPU: {cpu}%, RAM: {ram}%")
        return False
    return True

def run_file_safe(filepath):
    """
    Runs a Python file safely, catching errors, monitoring usage, and timeout.
    """
    if SAFE_MODE and not check_resources():
        print("⚠️  High resource usage — skipping execution.")
        return {"status": "skipped", "reason": "High usage"}

    print(f"🔒 Safe-running file: {filepath}")
    try:
        start = time.time()
        process = subprocess.run(
            ["python", filepath],
            capture_output=True,
            text=True,
            timeout=MAX_RUNTIME
        )
        duration = round(time.time() - start, 2)
        output = process.stdout
        error = process.stderr

        if process.returncode != 0:
            logging.error(f"Crash in {filepath} — {error.strip()}")
            return {"status": "error", "output": output, "error": error, "duration": duration}

        logging.info(f"Success: {filepath} ({duration}s)")
        return {"status": "success", "output": output, "duration": duration}

    except subprocess.TimeoutExpired:
        logging.warning(f"Timeout: {filepath} > {MAX_RUNTIME}s")
        return {"status": "timeout", "duration": MAX_RUNTIME}
    except Exception as e:
        logging.error(f"Exception running {filepath}: {e}")
        return {"status": "exception", "error": str(e)}
