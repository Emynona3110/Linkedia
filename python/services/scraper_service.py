import requests
from bs4 import BeautifulSoup
from core.icon_manager import fetch_icon_for_website


def scrape(url: str):
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=10,
        )
    except Exception:
        return {"error": "not_found"}

    if response.status_code == 404:
        return {"error": "not_found"}

    if response.status_code != 200:
        return {"error": "scrape_failed"}

    raw_html = response.content
    soup = BeautifulSoup(raw_html, "html.parser", from_encoding=None)

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = ""
    if desc_tag and desc_tag.get("content"):
        description = desc_tag["content"].strip()

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
