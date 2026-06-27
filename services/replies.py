"""Deterministic Telegram replies and alert image mappings."""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

from config import settings


@dataclass(frozen=True)
class ReplyDefinition:
    """Controlled text/image response for a known Telegram intent."""

    keywords: frozenset[str]
    text: str
    image: str


_WORD_RE = re.compile(r"[\wăâîșşțţ]+", re.IGNORECASE)


def normalize_message(text: str) -> str:
    """Normalize a Telegram message for exact controlled phrase matching."""
    normalized = unicodedata.normalize("NFKD", text.casefold())
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    words = _WORD_RE.findall(without_accents)
    return " ".join(words)


GREETING_REPLY = ReplyDefinition(
    keywords=frozenset(
        {
            "hi",
            "hello",
            "salut",
            "buna",
            "buna ziua",
        }
    ),
    text="🍺 <b>Salut, Raider!</b> Bine ai venit în taverna BeerGuy.",
    image="greeting.png",
)

GOOD_MORNING_REPLY = ReplyDefinition(
    keywords=frozenset(
        {
            "gm",
            "good morning",
            "buna dimineata",
        }
    ),
    text="☀️ <b>Good morning, Raider!</b> Taverna este deschisă.",
    image="good_morning.png",
)

GREETING_REPLIES = (GREETING_REPLY, GOOD_MORNING_REPLY)

ALERT_IMAGE_SETTINGS: dict[str, str] = {
    "BUY": "buy_image",
    "SELL": "sell_image",
    "BIG_BUY": "big_buy_image",
    "BIG_SELL": "big_sell_image",
    "LIQUIDITY": "liquidity_image",
    "NEW_HOLDER": "new_holder_image",
    "WHALE": "whale_image",
    "BURN": "burn_image",
    "PRICE_MILESTONE": "price_milestone_image",
    "HOLDER_MILESTONE": "holder_milestone_image",
}


def match_text_reply(text: str) -> ReplyDefinition | None:
    """Return a reply only when the whole message exactly matches a known phrase."""
    normalized = normalize_message(text)
    if not normalized:
        return None
    for reply in GREETING_REPLIES:
        if normalized in reply.keywords:
            return reply
    return None


def alert_image(alert_type: str) -> str:
    """Return the controlled image file for an alert type."""
    parts = [part for part in normalize_message(alert_type).split() if part != "alert"]
    key = "_".join(parts).upper()
    setting_name = ALERT_IMAGE_SETTINGS[key]
    return getattr(settings, setting_name)
