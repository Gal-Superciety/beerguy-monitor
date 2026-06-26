"""/chart command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from utils.branding import BEERGUY_MINT, official_links_keyboard, reply_branded_html, with_footer
from utils.formatters import solscan_token_url


async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the BeerGuy DexScreener chart."""
    if update.effective_message:
        chart_url = settings.dexscreener_url or solscan_token_url(settings.token_mint or BEERGUY_MINT)
        await reply_branded_html(
            update.effective_message,
            with_footer(f"📈 <b>BeerGuy Live Chart</b>\n\n<a href=\"{chart_url}\">Open Live Chart</a>"),
            reply_markup=official_links_keyboard(),
        )
