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

def build_entry_minimal(url: str) -> dict:
    return {
        "url": url,
        "title": url,
        "description_fr": "",
        "description_en": "",
        "tokens_en": "",
        "semantic": "",
        "icon": fetch_icon_for_website(url),
    }

def scrape(url: str) -> dict:
    fb = ddg_lookup(url)
    title_fb = fb.get("title") if fb else None
    desc_fb = fb.get("description") if fb else None

    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=SCRAPE_TIMEOUT)
        status = r.status_code
    except Exception:
        status = None
        r = None

    if status and status == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        for tag in soup.find_all("noscript"):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else title_fb
        meta = soup.find("meta", attrs={"name": "description"})
        desc = meta.get("content", "").strip() if meta else desc_fb

        if not desc:
            text = " ".join(soup.get_text(separator=" ").split())
            desc = text[:320] if text else desc_fb
    else:
        title = title_fb
        desc = desc_fb

    if not title and not desc:
        return build_entry_minimal(url)

    return build_entry(url, title, desc)
