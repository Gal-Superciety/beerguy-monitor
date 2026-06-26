"""/contract command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from utils.formatters import solscan_account_url


async def contract_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the BeerGuy token mint address."""
    await update.effective_message.reply_html(
        "🍺 <b>BEERGUY CONTRACT</b> 🍺\n\n"
        f"<code>{settings.token_mint}</code>\n\n"
        f"🔎 <a href=\"{solscan_account_url(settings.token_mint)}\">View on Solscan</a>"
    )
