# logger.py
# Appends every request to logs.txt and reads aggregate stats.

import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs.txt")


def log_request(prompt: str, status: str, score: int, ai_reason: str = "") -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = "─" * 60
    entry = (
        f"\n{separator}\n"
        f"[{timestamp}]  STATUS: {status}  SCORE: {score}%\n"
        f"PROMPT : {prompt[:300]}\n"
    )
    if ai_reason:
        entry += f"REASON : {ai_reason}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except IOError as e:
        print(f"[Logger] Could not write to {LOG_FILE}: {e}")


def read_stats() -> dict:
    stats = {"total": 0, "safe": 0, "suspicious": 0, "blocked": 0}
    if not os.path.exists(LOG_FILE):
        return stats
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "STATUS:" not in line:
                    continue
                stats["total"] += 1
                if "STATUS: SAFE" in line:
                    stats["safe"] += 1
                elif "STATUS: SUSPICIOUS" in line:
                    stats["suspicious"] += 1
                elif "STATUS: MALICIOUS" in line:
                    stats["blocked"] += 1
    except IOError:
        pass
    return stats
