import requests
from hashlib import md5
from urllib.parse import urlparse
from io import BytesIO

from PIL import Image

from core.paths import ICON_DIR

ICON_REQUEST_TIMEOUT = 6
ICON_SIZE = (32, 32)

FAVICON_SOURCES = [
    "https://{domain}/favicon.ico",
    "https://api.faviconkit.com/{domain}/64",
    "https://www.google.com/s2/favicons?domain={domain}&sz=64",
]


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
        r = requests.get(url, timeout=ICON_REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.content
    except Exception:
        return None


def save_as_png_32(data):
    try:
        img = Image.open(BytesIO(data)).convert("RGBA")
        img = img.resize(ICON_SIZE, Image.LANCZOS)
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

    for template in FAVICON_SOURCES:
        src = template.format(domain=domain)
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
