from rapidfuzz import fuzz
from core.data_manager import list_entries
from core.normalization import strip_accents


def search(query: str):
    query_norm = strip_accents(query.lower())

    data = list_entries()
    results = []

    for uid, entry in data.items():
        title = entry.get("title") or ""
        desc = entry.get("description") or ""
        content = entry.get("content") or ""

        haystack = " ".join([title, desc, content]).lower()
        haystack_norm = strip_accents(haystack)

        score = fuzz.partial_ratio(query_norm, haystack_norm)

        if score > 30:
            results.append((score, entry))

    results.sort(reverse=True, key=lambda x: x[0])
    return results
