import requests
from pathlib import Path
from hashlib import md5
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

BASE_DIR = Path(__file__).resolve().parents[2]
ICON_DIR = BASE_DIR / "data" / "icons"
ICON_DIR.mkdir(parents=True, exist_ok=True)


def get_icon_path(url: str):
    h = md5(url.encode()).hexdigest()
    return ICON_DIR / f"{h}.png"


def get_domain(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    if ":" in domain:
        domain = domain.split(":")[0]
    return domain


def build_google_favicon_url(domain: str, size: int = 64) -> str:
    return f"https://www.google.com/s2/favicons?domain={domain}&sz={size}"


def download_and_convert_icon(icon_url: str, dest: Path):
    try:
        r = requests.get(icon_url, timeout=5)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGBA")
        img = img.resize((18, 18))
        img.save(dest, format="PNG")
        return True
    except Exception:
        return False


def fetch_icon_for_website(url: str):
    domain = get_domain(url)
    if not domain:
        return None
    path = get_icon_path(url)
    if path.exists():
        return str(path)
    icon_url = build_google_favicon_url(domain)
    ok = download_and_convert_icon(icon_url, path)
    if ok:
        return str(path)
    return None
