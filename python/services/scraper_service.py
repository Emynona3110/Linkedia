import requests
from bs4 import BeautifulSoup
from core.icon_manager import fetch_icon_for_website
from services.search_fallback import ddg_lookup
from core.translation import translate_to_french


def scrape(url: str):
    fallback = ddg_lookup(url)

    if fallback and fallback.get("description"):
        title = fallback.get("title") or ""
        description = fallback.get("description") or ""
        content = description

        title = translate_to_french(title)
        description = translate_to_french(description)
        content = translate_to_french(content)

        return {
            "url": url,
            "title": title,
            "description": description,
            "content": content,
            "icon": fetch_icon_for_website(url)
        }

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            raise Exception()
    except Exception:
        if fallback:
            title = fallback.get("title") or ""
            description = fallback.get("description") or ""
            content = description

            title = translate_to_french(title)
            description = translate_to_french(description)
            content = translate_to_french(content)

            return {
                "url": url,
                "title": title,
                "description": description,
                "content": content,
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

    content = description

    title = translate_to_french(title)
    description = translate_to_french(description)
    content = translate_to_french(content)

    return {
        "url": url,
        "title": title,
        "description": description,
        "content": content,
        "icon": fetch_icon_for_website(url)
    }
