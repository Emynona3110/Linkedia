from deep_translator import GoogleTranslator
from rank_bm25 import BM25Okapi
from nltk.stem.snowball import SnowballStemmer

from core.data_manager import list_entries
from core.normalization import clean_word

stemmer = SnowballStemmer("english")

def tokenize(text: str):
    out = []
    for w in text.split():
        c = clean_word(w)
        if not c:
            continue
        out.append(stemmer.stem(c))
    return out

def build_document(entry):
    title = entry.get("title", "")
    desc_en = entry.get("description_en", "")
    desc_fr = entry.get("description_fr", "")
    tokens_en = entry.get("tokens_en", "")
    semantic = entry.get("semantic", "")

    t = tokenize(title) * 3
    e = tokenize(desc_en) * 3
    k = tokenize(tokens_en)
    s = tokenize(semantic)
    f = tokenize(desc_fr)

    return t + e + k + s + f

def search(query: str):
    translated = GoogleTranslator(source="fr", target="en").translate(query).lower()
    q_tokens = tokenize(translated)

    print("Recherche FR :", query)
    print("Traduction EN :", translated)
    print("Tokens utilisés :", q_tokens)
    print("-" * 40)

    data = list_entries()
    entries = list(data.values())

    corpus = [build_document(e) for e in entries]
    bm25 = BM25Okapi(corpus)

    scores = bm25.get_scores(q_tokens)
    ranked = sorted(zip(scores, entries), key=lambda x: x[0], reverse=True)

    return [(s, e) for s, e in ranked if s > 0]
