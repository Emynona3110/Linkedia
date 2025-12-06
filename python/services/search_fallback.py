import requests
from bs4 import BeautifulSoup
from pathlib import Path
from hashlib import md5

BASE_DIR = Path(__file__).resolve().parents[2]
ICON_DIR = BASE_DIR / "data" / "icons"
ICON_DIR.mkdir(parents=True, exist_ok=True)

def ddg_lookup(query: str):
    r = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    result = soup.select_one(".result")
    if not result:
        return None

    title_tag = result.select_one(".result__title a")
    snippet_tag = result.select_one(".result__snippet")
    icon_tag = result.select_one("img.result_icon_img")

    icon_url = None
    if icon_tag and icon_tag.get("src"):
        url = icon_tag["src"]
        if url.startswith("//"):
            url = "https:" + url
        icon_url = url

    icon_path = None
    if icon_url:
        h = md5(query.encode()).hexdigest()
        dest = ICON_DIR / f"{h}.png"
        try:
            img_data = requests.get(icon_url, timeout=5).content
            with open(dest, "wb") as f:
                f.write(img_data)
            icon_path = str(dest)
        except Exception:
            icon_path = None

    return {
        "title": title_tag.get_text(strip=True) if title_tag else None,
        "url": title_tag["href"] if title_tag and title_tag.get("href") else None,
        "description": snippet_tag.get_text(strip=True) if snippet_tag else None,
        "icon": icon_path,
    }
