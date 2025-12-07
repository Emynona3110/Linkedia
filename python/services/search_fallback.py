import requests
from bs4 import BeautifulSoup
from hashlib import md5

from core.paths import ICON_DIR

DDG_SEARCH_URL = "https://duckduckgo.com/html/"
USER_AGENT = "Mozilla/5.0"
SEARCH_TIMEOUT = 8
ICON_TIMEOUT = 5


def ddg_lookup(query: str):
    r = requests.get(
        DDG_SEARCH_URL,
        params={"q": query},
        timeout=SEARCH_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )
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
            img_data = requests.get(icon_url, timeout=ICON_TIMEOUT).content
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
