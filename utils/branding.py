"""BeerGuy branding, message, and inline keyboard helpers."""
from __future__ import annotations

from collections.abc import Sequence

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import settings
from utils.formatters import solscan_token_url
from utils.images import image_path

BEERGUY_NAME = "BeerGuy"
BEERGUY_TICKER = "BGUY"
BEERGUY_NETWORK = "Solana"
BEERGUY_MINT = "7mF2JsRcr5MfeTQKkhMM8dZQSRvkpsnxeM23onzbBtuH"
BEERGUY_CREATED = "June 18, 2026"
BEERGUY_FOOTER = "⚔️ Brew. Farm. Raid."
BEERGUY_TAGLINE = "The legendary beer spirit of crypto."
BEERGUY_COLORS = "🍺 Gold • ⚔️ Viking Bronze • 🖤 Midnight Ale"

WEBSITE_URL = "https://beerguy.io/"
TWITTER_URL = "https://x.com/BeerGuyOfficial"
TELEGRAM_URL = "https://t.me/BeerGuyRaiders"


def official_links_keyboard(include_contract_callback: bool = True) -> InlineKeyboardMarkup:
    """Return reusable BeerGuy inline buttons for community commands."""
    chart_url = settings.dexscreener_url or solscan_token_url(settings.token_mint or BEERGUY_MINT)
    contract_button = (
        InlineKeyboardButton("📄 Smart Contract", callback_data="show_contract")
        if include_contract_callback
        else InlineKeyboardButton("📄 Smart Contract", url=solscan_token_url(settings.token_mint or BEERGUY_MINT))
    )
    rows: Sequence[Sequence[InlineKeyboardButton]] = (
        (
            InlineKeyboardButton("🌐 Official Website", url=WEBSITE_URL),
            InlineKeyboardButton("🐦 X (Twitter)", url=TWITTER_URL),
        ),
        (
            InlineKeyboardButton("💬 Telegram Community", url=TELEGRAM_URL),
            InlineKeyboardButton("📈 Live Chart", url=chart_url),
        ),
        (
            contract_button,
            InlineKeyboardButton("🔎 Solscan", url=solscan_token_url(settings.token_mint or BEERGUY_MINT)),
        ),
    )
    return InlineKeyboardMarkup(rows)


def with_footer(body: str) -> str:
    """Append the standard BeerGuy footer."""
    return f"{body.rstrip()}\n\n{BEERGUY_FOOTER}"


async def reply_branded_html(
    message: Message,
    html: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    logo: bool = True,
) -> None:
    """Reply with the BeerGuy logo when available, falling back to HTML text."""
    path = image_path("logo.png") if logo else None
    if path:
        with path.open("rb") as photo:
            await message.reply_photo(photo=photo, caption=html, parse_mode="HTML", reply_markup=reply_markup)
        return
    await message.reply_html(html, reply_markup=reply_markup, disable_web_page_preview=True)
