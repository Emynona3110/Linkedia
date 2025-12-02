import requests
from bs4 import BeautifulSoup

def scrape(url: str):
    try:
        response = requests.get(url, headers={"User-Agent": "LinkediaBot/1.0"}, timeout=10)
    except Exception:
        return None
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag["content"].strip() if desc_tag else ""
    for tag in soup(["script", "style"]):
        tag.decompose()
    content = soup.get_text(separator=" ", strip=True)
    return {"url": url, "title": title, "description": description, "content": content[:30000]}
