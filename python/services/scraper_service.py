import requests
from bs4 import BeautifulSoup


def scrape(url: str):
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "LinkediaBot/1.0"},
            timeout=10,
        )
    except Exception:
        return None
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

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

    return {
        "url": url,
        "title": title,
        "description": description,
        "content": content,
    }
