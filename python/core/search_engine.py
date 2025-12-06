from rapidfuzz import fuzz
from core.data_manager import list_entries
from deep_translator import GoogleTranslator

def clean_word(w):
    w = "".join(c for c in w.lower() if c.isalpha())
    return w if w else ""

def tokenize(q):
    raw = q.split()
    out = []
    for w in raw:
        x = clean_word(w)
        if x:
            out.append(x)
    return out

def search(query: str):
    q_en = GoogleTranslator(source="auto", target="en").translate(query).lower()
    q_tokens = tokenize(q_en)
    data = list_entries()
    results = []

    for uid, entry in data.items():
        tokens = entry.get("content", "").split()
        title = entry.get("title", "").lower()
        score = 0
        matched = 0

        for q in q_tokens:
            if q in tokens:
                score += 100
                matched += 1
            else:
                fuzz_scores = [fuzz.partial_ratio(q, t) for t in tokens]
                if fuzz_scores:
                    fs = max(fuzz_scores)
                    score += min(fs * 0.3, 20)
            if q in title:
                score += 40

        if len(q_tokens) > 1:
            score += len(q_tokens) * 15

        if tokens:
            density = matched / len(tokens)
            score += density * 200

        if score > 5:
            results.append((score, entry))

    results.sort(reverse=True, key=lambda x: x[0])
    return results
