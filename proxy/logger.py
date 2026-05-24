import json
import os
import threading
from datetime import datetime, timezone

LOGS_DIR = "logs"
LOGS_FILE = "logs/log.json"
_lock = threading.Lock()

def log_access(url: str, action: str) -> None:
    os.makedirs(LOGS_DIR, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": url,
        "action": action
    }

    with _lock:
        logs = []
        if os.path.exists(LOGS_FILE):
            try:
                with open(LOGS_FILE, "r") as f:
                    content = f.read().strip()
                    if content:
                        logs = json.loads(content)
            except (json.JSONDecodeError, ValueError):
                logs = []

        logs.append(entry)

        with open(LOGS_FILE, "w") as f:
            json.dump(logs, f, indent=2)