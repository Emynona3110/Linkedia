import json
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
INDEX_FILE = DATA_DIR / "index.json"


def load_index():
    if not INDEX_FILE.exists():
        return {}
    with INDEX_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_index(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with INDEX_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def hash_url(url: str):
    return hashlib.md5(url.encode()).hexdigest()


def add_or_update_entry(entry: dict):
    data = load_index()
    uid = hash_url(entry["url"])
    data[uid] = entry
    save_index(data)


def delete_entry(url: str):
    data = load_index()
    uid = hash_url(url)
    if uid in data:
        icon = data[uid].get("icon")
        if icon:
            p = Path(icon)
            if p.exists():
                try:
                    p.unlink()
                except:
                    pass
        del data[uid]
        save_index(data)
        return True
    return False


def list_entries():
    return load_index()


def get_entry(url: str):
    data = load_index()
    uid = hash_url(url)
    return data.get(uid)
