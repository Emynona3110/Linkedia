from rapidfuzz import fuzz
from storage import list_entries

def search(query: str):
    data = list_entries()
    results = []
    for uid, entry in data.items():
        haystack = " ".join([entry.get("title") or "",entry.get("description") or "",entry.get("content") or ""])
        score = fuzz.partial_ratio(query.lower(), haystack.lower())
        if score > 30:
            results.append((score, entry))
    results.sort(reverse=True, key=lambda x: x[0])
    return results
