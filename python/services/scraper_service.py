import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from core.icon_manager import fetch_icon_for_website
from services.search_fallback import ddg_lookup
from core.translation import translate_to_french

STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "your", "yours", "their",
    "there", "been", "into", "onto", "about", "above", "below", "under", "over",
    "very", "much", "make", "makes", "made", "some", "many", "most", "such", "than",
    "then", "they", "them", "were", "was", "are", "have", "here", "where", "when",
    "who", "whom", "what", "why", "how", "one", "two", "three", "new", "news",
    "like", "also", "more", "less", "just", "even", "only", "each", "other",
    "others", "own", "same", "any", "all", "you", "we", "it", "its", "our", "of",
    "in", "on", "to", "as", "at", "by", "be", "is", "an", "a"
}

def clean_word(w: str) -> str:
    w = "".join(c for c in w.lower() if c.isalpha())
    if not w:
        return ""
    if w in STOPWORDS:
        return ""
    return w

def datamuse_related(term: str, limit: int = 20) -> list[str]:
    try:
        r = requests.get(
            "https://api.datamuse.com/words",
            params={"ml": term, "max": limit},
            timeout=5,
        )
        data = r.json()
        out: list[str] = []
        for item in data:
            w = clean_word(item.get("word", ""))
            if w:
                out.append(w)
        return out
    except Exception:
        return []

def get_content_from_desc(desc: str) -> str:
    en = GoogleTranslator(source="auto", target="en").translate(desc)
    base_words = [clean_word(w) for w in en.split()]
    base_words = [w for w in base_words if w]
    if not base_words:
        return ""

    related_words: list[str] = []
    for w in base_words:
        related_words.extend(datamuse_related(w, limit=20))

    all_words = sorted(set(base_words + related_words))
    return " ".join(all_words)

def build_entry(url: str, title: str, description: str) -> dict:
    fr_title = translate_to_french(title)
    fr_desc = translate_to_french(description)
    content = get_content_from_desc(fr_desc)
    return {
        "url": url,
        "title": fr_title,
        "description": fr_desc,
        "content": content,
        "icon": fetch_icon_for_website(url),
    }

def scrape(url: str) -> dict:
    fb = ddg_lookup(url)
    if fb and fb.get("description"):
        return build_entry(url, fb.get("title") or "", fb.get("description") or "")

    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if r.status_code != 200:
            raise Exception()
    except Exception:
        if fb:
            return build_entry(url, fb.get("title") or "", fb.get("description") or "")
        return {"error": "not_found"}

    soup = BeautifulSoup(r.content, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    tag = soup.find("meta", attrs={"name": "description"})
    desc = tag.get("content", "").strip() if tag else ""

    text = " ".join(soup.get_text(separator=" ").split())
    if not desc and text:
        desc = text[:320]

    return build_entry(url, title, desc)
