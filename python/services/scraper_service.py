import requests
from bs4 import BeautifulSoup
from services.search_fallback import ddg_lookup
from core.icon_manager import fetch_icon_for_website

def scrape(url: str):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    except Exception:
        fallback = ddg_lookup(url)
        if fallback:
            fallback["url"] = url
            fallback["icon"] = fetch_icon_for_website(url)
            fallback["content"] = ""
            return fallback
        return {"error": "not_found"}

    if response.status_code != 200:
        fallback = ddg_lookup(url)
        if fallback:
            fallback["url"] = url
            fallback["icon"] = fetch_icon_for_website(url)
            fallback["content"] = ""
            return fallback
        return {"error": "scrape_failed"}

    raw_html = response.content
    soup = BeautifulSoup(raw_html, "html.parser", from_encoding=None)

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    content = " ".join(text.split())
    if not description and content:
        description = content[:320]
    if content and len(content) > 30000:
        content = content[:30000]

    icon_local_path = fetch_icon_for_website(url)

    return {
        "url": url,
        "title": title,
        "description": description,
        "content": content,
        "icon": icon_local_path,
    }
