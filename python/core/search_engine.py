from rapidfuzz import fuzz
from core.data_manager import list_entries
from core.normalization import strip_accents
from .translation import translate_to_french, translate_to_english


def search(query: str):
    query_norm = strip_accents(query.lower())

    query_fr = translate_to_french(query) if query.strip() else ""
    query_en = translate_to_english(query) if query.strip() else ""

    query_fr_norm = strip_accents(query_fr.lower()) if query_fr else ""
    query_en_norm = strip_accents(query_en.lower()) if query_en else ""

    data = list_entries()
    results = []

    for uid, entry in data.items():
        title = entry.get("title") or ""
        desc = entry.get("description") or ""
        content = entry.get("content") or ""

        haystack = " ".join([title, desc, content]).lower()
        haystack_norm = strip_accents(haystack)

        s1 = fuzz.partial_ratio(query_norm, haystack_norm)
        s2 = fuzz.partial_ratio(query_fr_norm, haystack_norm) if query_fr_norm else 0
        s3 = fuzz.partial_ratio(query_en_norm, haystack_norm) if query_en_norm else 0

        score = max(s1, s2, s3)

        if score > 30:
            results.append((score, entry))

    results.sort(reverse=True, key=lambda x: x[0])
    return results
