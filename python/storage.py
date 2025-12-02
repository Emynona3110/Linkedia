import json, os, hashlib

INDEX_FILE = "index.json"

def load_index():
    if not os.path.exists(INDEX_FILE):
        return {}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_index(data):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_url(url: str):
    return hashlib.md5(url.encode()).hexdigest()

def add_or_update_entry(entry):
    data = load_index()
    uid = hash_url(entry["url"])
    data[uid] = entry
    save_index(data)

def delete_entry(url: str):
    data = load_index()
    uid = hash_url(url)
    if uid in data:
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
