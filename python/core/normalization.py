import unicodedata
from core.data_manager import get_entry


def strip_accents(text: str):
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def normalize_entry(raw):
    if isinstance(raw, dict):
        title = raw.get("title") or raw.get("url") or ""
        url = raw.get("url") or ""
        description = raw.get("description") or ""
        return {
            "title": title,
            "url": url,
            "description": description
        }

    key = str(raw)
    entry = get_entry(key)
    if isinstance(entry, dict):
        return normalize_entry(entry)

    return {"title": key, "url": key, "description": ""}
