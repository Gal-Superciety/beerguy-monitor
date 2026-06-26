"""Reusable BeerGuy inline keyboards."""
from __future__ import annotations

from collections.abc import Sequence

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import settings
from utils.formatters import solscan_token_url

BEERGUY_MINT = "7mF2JsRcr5MfeTQKkhMM8dZQSRvkpsnxeM23onzbBtuH"
WEBSITE_URL = "https://beerguy.io/"
TWITTER_URL = "https://x.com/BeerGuyOfficial"
TELEGRAM_URL = "https://t.me/BeerGuyRaiders"


def official_links_keyboard(include_contract_callback: bool = True) -> InlineKeyboardMarkup:
    """Return reusable BeerGuy inline buttons for community commands."""
    token_mint = settings.token_mint or BEERGUY_MINT
    chart_url = settings.dexscreener_url or solscan_token_url(token_mint)
    contract_button = (
        InlineKeyboardButton("📄 Smart Contract", callback_data="show_contract")
        if include_contract_callback
        else InlineKeyboardButton("📄 Smart Contract", url=solscan_token_url(token_mint))
    )
    rows: Sequence[Sequence[InlineKeyboardButton]] = (
        (
            InlineKeyboardButton("🌐 Website", url=WEBSITE_URL),
            InlineKeyboardButton("🐦 X", url=TWITTER_URL),
        ),
        (
            InlineKeyboardButton("💬 Telegram", url=TELEGRAM_URL),
            InlineKeyboardButton("📈 Chart", url=chart_url),
        ),
        (contract_button,),
    )
    return InlineKeyboardMarkup(rows)
