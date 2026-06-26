"""Central logging setup for the bot."""
from __future__ import annotations

import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configure consistent console logging."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
