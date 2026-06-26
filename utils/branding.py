"""BeerGuy branding, message, and inline keyboard helpers."""
from __future__ import annotations

from telegram import InlineKeyboardMarkup, Message

from utils.keyboards import BEERGUY_MINT, official_links_keyboard
from utils.images import image_path

BEERGUY_NAME = "BeerGuy"
BEERGUY_TICKER = "BGUY"
BEERGUY_NETWORK = "Solana"
BEERGUY_CREATED = "June 18, 2026"
BEERGUY_FOOTER = "⚔️ Brew. Farm. Raid."
BEERGUY_TAGLINE = "The legendary beer spirit of crypto."
BEERGUY_COLORS = "🍺 Gold • ⚔️ Viking Bronze • 🖤 Midnight Ale"



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
