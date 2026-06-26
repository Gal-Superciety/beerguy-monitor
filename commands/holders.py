"""/holders command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from services.holders import HolderService
from utils.formatters import format_number


async def holders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send holder and supply information."""
    service: HolderService = context.application.bot_data["holder_service"]
    stats = await service.stats()
    await update.effective_message.reply_text(
        "🍺 BEERGUY HOLDERS 🍺\n\n"
        f"🏦 Largest tracked accounts: {stats.largest_accounts}\n"
        f"🪙 Supply: {format_number(stats.supply, 2)} BGUY\n\n"
        "⚔️ Brew. Farm. Raid."
    )
