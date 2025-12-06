import requests
from bs4 import BeautifulSoup
from core.icon_manager import fetch_icon_for_website
from services.search_fallback import ddg_lookup


def scrape(url: str):
    fallback = ddg_lookup(url)

    if fallback and fallback.get("description"):
        return {
            "url": url,
            "title": fallback.get("title") or "",
            "description": fallback.get("description") or "",
            "content": fallback.get("description") or "",
            "icon": fetch_icon_for_website(url)
        }

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            raise Exception()
    except Exception:
        if fallback:
            return {
                "url": url,
                "title": fallback.get("title") or "",
                "description": fallback.get("description") or "",
                "content": fallback.get("description") or "",
                "icon": fetch_icon_for_website(url)
            }
        return {"error": "not_found"}

    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag.get("content", "").strip() if desc_tag else ""

    text = " ".join(soup.get_text(separator=" ").split())

    if not description and text:
        description = text[:320]

    return {
        "url": url,
        "title": title,
        "description": description,
        "content": description,
        "icon": fetch_icon_for_website(url)
    }
