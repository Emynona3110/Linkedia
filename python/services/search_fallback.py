import requests
from bs4 import BeautifulSoup
from hashlib import md5

from core.paths import ICON_DIR, relative_icon_path

DDG_SEARCH_URL = "https://duckduckgo.com/html/"
USER_AGENT = "Mozilla/5.0"
SEARCH_TIMEOUT = 8
ICON_TIMEOUT = 5


def ddg_lookup(query: str):
    try:
        r = requests.get(
            DDG_SEARCH_URL,
            params={"q": query},
            timeout=SEARCH_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
    except:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    icon_tag = soup.select_one("img.result_icon_img")

    if icon_tag and icon_tag.get("src"):
        icon_url = icon_tag["src"]
        if icon_url.startswith("//"):
            icon_url = "https:" + icon_url

        h = md5(query.encode()).hexdigest()
        dest = ICON_DIR / f"{h}.png"
        try:
            data = requests.get(icon_url, timeout=ICON_TIMEOUT).content
            with open(dest, "wb") as f:
                f.write(data)
            return {"icon": relative_icon_path(f"{h}.png")}
        except:
            return None

    return None
