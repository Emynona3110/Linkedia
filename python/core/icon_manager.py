import requests
from pathlib import Path
from hashlib import md5
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

BASE_DIR = Path(__file__).resolve().parents[2]
ICON_DIR = BASE_DIR / "data" / "icons"
ICON_DIR.mkdir(parents=True, exist_ok=True)


def get_domain(url: str):
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    if ":" in domain:
        domain = domain.split(":")[0]
    return domain


def icon_path(url: str):
    h = md5(url.encode()).hexdigest()
    return ICON_DIR / f"{h}.png"


def try_download(url: str):
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        return r.content
    except Exception:
        return None


def save_as_png_32(data):
    try:
        img = Image.open(BytesIO(data)).convert("RGBA")
        img = img.resize((32, 32), Image.LANCZOS)
        out = BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
    except Exception:
        return None


def fetch_icon_for_website(url: str):
    domain = get_domain(url)
    if not domain:
        return None

    dest = icon_path(url)

    sources = [
        f"https://{domain}/favicon.ico",
        f"https://api.faviconkit.com/{domain}/64",
        f"https://www.google.com/s2/favicons?domain={domain}&sz=64",
    ]

    for src in sources:
        data = try_download(src)
        if not data:
            continue

        png_bytes = save_as_png_32(data)
        if not png_bytes:
            continue

        with open(dest, "wb") as f:
            f.write(png_bytes)

        return str(dest)

    return None
