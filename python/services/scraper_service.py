import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

from core.icon_manager import fetch_icon_for_website
from services.search_fallback import ddg_lookup
from core.translation import translate_to_french
from core.normalization import clean_word

DATAMUSE_URL = "https://api.datamuse.com/words"
DATAMUSE_TIMEOUT = 5
SCRAPE_TIMEOUT = 8

SEM_LIMIT = 5
SEM_BASE_WORDS = 8

def datamuse_related(term: str, limit: int = SEM_LIMIT) -> list[str]:
    try:
        r = requests.get(DATAMUSE_URL, params={"ml": term, "max": limit}, timeout=DATAMUSE_TIMEOUT)
        data = r.json()
        out = []
        for item in data:
            w = clean_word(item.get("word", ""))
            if w:
                out.append(w)
        return out
    except:
        return []

def get_tokens_from_desc(desc: str) -> list[str]:
    en = GoogleTranslator(source="auto", target="en").translate(desc)
    return [clean_word(w) for w in en.split() if clean_word(w)]

def get_semantic(tokens: list[str]) -> list[str]:
    related = []
    for w in tokens[:SEM_BASE_WORDS]:
        related.extend(datamuse_related(w, SEM_LIMIT))
    return sorted(set(clean_word(w) for w in related if clean_word(w)))

def build_entry(url: str, title: str, description: str) -> dict:
    description_en = GoogleTranslator(source="auto", target="en").translate(description)
    description_fr = translate_to_french(description)

    tokens_en = get_tokens_from_desc(description_en)
    semantic = get_semantic(tokens_en)

    return {
        "url": url,
        "title": translate_to_french(title),
        "description_fr": description_fr,
        "description_en": description_en,
        "tokens_en": " ".join(tokens_en),
        "semantic": " ".join(semantic),
        "icon": fetch_icon_for_website(url),
    }

def scrape(url: str) -> dict:
    fb = ddg_lookup(url)
    if fb and (fb.get("title") or fb.get("description")):
        return build_entry(url, fb.get("title") or "", fb.get("description") or "")

    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=SCRAPE_TIMEOUT)
        if r.status_code != 200:
            raise Exception()
    except:
        if fb:
            return build_entry(url, fb.get("title") or "", fb.get("description") or "")
        return {"error": "not_found"}

    soup = BeautifulSoup(r.content, "html.parser")
    for tag in soup.find_all("noscript"):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta = soup.find("meta", attrs={"name": "description"})
    desc = meta.get("content", "").strip() if meta else ""

    if not title and not desc and fb:
        return build_entry(url, fb.get("title") or "", fb.get("description") or "")

    text = " ".join(soup.get_text(separator=" ").split())
    if not desc and text:
        desc = text[:320]

    return build_entry(url, title, desc)
