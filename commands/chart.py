"""/chart command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings


async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the BeerGuy DexScreener chart."""
    await update.effective_message.reply_html(f"📈 <a href=\"{settings.dexscreener_url}\">BeerGuy Chart</a>\n\n⚔️ Brew. Farm. Raid.")
