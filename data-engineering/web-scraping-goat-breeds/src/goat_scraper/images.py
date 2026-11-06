"""Download breed images with safe file names."""
import re
import time
from pathlib import Path

from .parse import Breed


def slugify(name: str, fallback: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    return slug or fallback


def download_images(breeds: list[Breed], out_dir: Path, session, delay: float = 0.3, timeout: float = 20) -> dict:
    """Returns {breed name: local path or ''}. Already downloaded files are skipped."""
    out_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, str] = {}
    for i, breed in enumerate(breeds):
        result[breed.name] = ""
        if not breed.image_url:
            continue
        target = out_dir / f"{slugify(breed.name, f'breed_{i}')}.jpg"
        if target.exists():
            result[breed.name] = str(target)
            continue
        try:
            response = session.get(breed.image_url, timeout=timeout)
            response.raise_for_status()
        except Exception:
            continue
        target.write_bytes(response.content)
        result[breed.name] = str(target)
        time.sleep(delay)  # be polite to the server
    return result
