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

def normalize_entry(raw):
    if isinstance(raw, dict):
        return {
            "title": raw.get("title") or raw.get("url") or "",
            "url": raw.get("url") or "",
            "description_fr": raw.get("description_fr") or "",
            "description_en": raw.get("description_en") or "",
            "tokens_en": raw.get("tokens_en", ""),
            "semantic": raw.get("semantic", ""),
            "icon": raw.get("icon"),
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
        "tokens_en": "",
        "semantic": "",
        "icon": None,
    }
