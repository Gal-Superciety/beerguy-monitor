"""Asset lookup helpers for Telegram photo alerts."""
from __future__ import annotations

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
IMAGES_DIR = ASSETS_DIR / "images"


def image_path(name: str | None) -> Path | None:
    """Return an image asset path if it exists, otherwise None.

    Environment variables should contain image file names such as ``buy.png``.
    Only the basename is used so alerts always resolve inside ``assets/images``
    and never depend on images stored at the repository root.
    """
    if not name:
        return None
    filename = Path(name).name
    if not filename:
        return None
    path = IMAGES_DIR / filename
    return path if path.exists() and path.stat().st_size > 0 else None
