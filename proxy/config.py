import json
import os

def load_configs() -> tuple[list, dict]:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    blocked_path = os.path.join(base_dir, "config", "blocked.json")
    words_path   = os.path.join(base_dir, "config", "words.json")

    blocked_list = []
    words_dict   = {}

    try:
        with open(blocked_path, "r", encoding="utf-8") as f:
            blocked_list = json.load(f).get("bloqueados", [])
    except FileNotFoundError:
        print(f"[config] {blocked_path} not found.")

    try:
        with open(words_path, "r", encoding="utf-8") as f:
            words_dict = json.load(f)
    except FileNotFoundError:
        print(f"[config] {words_path} not found.")

    return blocked_list, words_dict

if __name__ == "__main__":
    blocked, words = load_configs()
    print("Blocked list:", blocked)
    print("Words dict:",   words)