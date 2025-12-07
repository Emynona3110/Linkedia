from rapidfuzz import fuzz
from deep_translator import GoogleTranslator

from core.data_manager import list_entries

FUZZ_WEIGHT = 0.3
FUZZ_MAX_BONUS = 20
EXACT_CONTENT_SCORE = 100
TITLE_MATCH_SCORE = 40
MULTI_TOKEN_BONUS = 15
DENSITY_FACTOR = 200
MIN_SCORE = 5


def clean_word(w):
    w = "".join(c for c in w.lower() if c.isalpha())
    return w if w else ""


def tokenize(text):
    return [clean_word(w) for w in text.split() if clean_word(w)]


def search(query: str):
    translated = GoogleTranslator(source="fr", target="en").translate(query).lower()
    q_tokens = tokenize(translated)

    data = list_entries()
    results = []

    for uid, entry in data.items():
        content_tokens = tokenize(entry.get("content", "").lower())
        title_tokens = tokenize(entry.get("title", "").lower())

        score = 0
        matched = 0

        for q in q_tokens:
            if q in content_tokens:
                score += EXACT_CONTENT_SCORE
                matched += 1
            else:
                fuzz_scores = [fuzz.partial_ratio(q, t) for t in content_tokens]
                if fuzz_scores:
                    score += min(max(fuzz_scores) * FUZZ_WEIGHT, FUZZ_MAX_BONUS)

            if q in title_tokens:
                score += TITLE_MATCH_SCORE

        if len(q_tokens) > 1:
            score += len(q_tokens) * MULTI_TOKEN_BONUS

        if content_tokens:
            density = matched / len(content_tokens)
            score += density * DENSITY_FACTOR

        if score > MIN_SCORE:
            results.append((score, entry))

    results.sort(reverse=True, key=lambda x: x[0])
    return results
