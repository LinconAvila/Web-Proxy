import json
import os
from datetime import datetime, timezone

LOGS_DIR = "logs"
LOGS_FILE = "logs/log.json"

def log_access(url: str, action: str) -> None:
    os.makedirs(LOGS_DIR, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": url,
        "action": action
    }

    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(entry)

    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2)