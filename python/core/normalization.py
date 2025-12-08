import unicodedata
from core.data_manager import get_entry

STOPWORDS = {
    "the","and","for","with","from","that","this","your","yours","their","there","been",
    "into","onto","about","above","below","under","over","very","much","make","makes",
    "made","some","many","most","such","than","then","they","them","were","was","are",
    "have","here","where","when","who","whom","what","why","how","one","two","three",
    "new","news","like","also","more","less","just","even","only","each","other","others",
    "own","same","any","all","you","we","it","its","our","of","in","on","to","as","at",
    "by","be","is","an","a"
}

def strip_accents(text: str):
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

def clean_word(w: str) -> str:
    w = "".join(c for c in w.lower() if c.isalpha())
    if not w or w in STOPWORDS:
        return ""
    return w

def stem(w: str) -> str:
    if len(w) <= 3:
        return w
    if w.endswith("ing"):
        w = w[:-3]
    elif w.endswith("ers"):
        w = w[:-3]
    elif w.endswith("er"):
        w = w[:-2]
    elif w.endswith("ed"):
        w = w[:-2]
    if w.endswith("s") and len(w) > 3:
        w = w[:-1]
    return w

def normalize_entry(raw):
    if isinstance(raw, dict):
        return {
            "title": raw.get("title") or raw.get("url") or "",
            "url": raw.get("url") or "",
            "description_fr": raw.get("description_fr") or raw.get("description") or "",
            "description_en": raw.get("description_en") or raw.get("description") or "",
            "icon": raw.get("icon"),
            "content": raw.get("content") or "",
        }
    key = str(raw)
    entry = get_entry(key)
    if isinstance(entry, dict):
        return normalize_entry(entry)
    return {
        "title": key,
        "url": key,
        "description_fr": "",
        "description_en": "",
        "icon": None,
        "content": "",
    }
