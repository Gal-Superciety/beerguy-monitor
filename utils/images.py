"""Asset lookup helpers for Telegram photo alerts."""
from __future__ import annotations

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def image_path(name: str) -> Path | None:
    """Return an asset path if it exists, otherwise None."""
    path = ASSETS_DIR / name
    return path if path.exists() and path.stat().st_size > 0 else None
