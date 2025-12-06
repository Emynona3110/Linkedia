from rapidfuzz import fuzz
from core.data_manager import list_entries
from deep_translator import GoogleTranslator

def clean_word(w):
    w = "".join(c for c in w.lower() if c.isalpha())
    return w if w else ""

def tokenize(text):
    return [clean_word(w) for w in text.split() if clean_word(w)]

def search(query: str):
    translated = GoogleTranslator(source="fr", target="en").translate(query).lower()
    print("Query FR :", query)
    print("Query EN :", translated)

    q_tokens = tokenize(translated)
    print("Tokens :", q_tokens)

    data = list_entries()
    results = []

    for uid, entry in data.items():
        content_tokens = tokenize(entry.get("content", "").lower())
        title_tokens = tokenize(entry.get("title", "").lower())

        score = 0
        matched = 0

        for q in q_tokens:
            if q in content_tokens:
                score += 100
                matched += 1
            else:
                fuzz_scores = [fuzz.partial_ratio(q, t) for t in content_tokens]
                if fuzz_scores:
                    score += min(max(fuzz_scores) * 0.3, 20)

            if q in title_tokens:
                score += 40

        if len(q_tokens) > 1:
            score += len(q_tokens) * 15

        if content_tokens:
            density = matched / len(content_tokens)
            score += density * 200

        if score > 5:
            results.append((score, entry))

    results.sort(reverse=True, key=lambda x: x[0])
    return results
