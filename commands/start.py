"""/start command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from utils.branding import (
    BEERGUY_COLORS,
    BEERGUY_FOOTER,
    BEERGUY_NETWORK,
    BEERGUY_TAGLINE,
    BEERGUY_TICKER,
    official_links_keyboard,
    reply_branded_html,
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a professional BeerGuy community welcome message."""
    message = update.effective_message
    if message is None:
        return
    await reply_branded_html(
        message,
        "🍺 <b>BeerGuy</b>\n\n"
        f"🪙 <b>Ticker:</b> {BEERGUY_TICKER}\n"
        f"🌐 <b>Network:</b> {BEERGUY_NETWORK}\n\n"
        "<b>Description:</b>\n"
        f"{BEERGUY_TAGLINE}\n\n"
        "Born in the hop fields.\n"
        "Raised by Vikings.\n"
        "Built for the Beer Raiders.\n\n"
        f"🎨 <b>Colors:</b> {BEERGUY_COLORS}\n\n"
        "Welcome to the official BeerGuy community monitor for market snapshots, holder stats, raids, and future live alerts.\n\n"
        f"{BEERGUY_FOOTER}",
        reply_markup=official_links_keyboard(),
    )
