"""/raid command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def raid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Rally the BeerGuy community."""
    await update.effective_message.reply_text(
        "⚔️ BEER RAID CALLED ⚔️\n\n"
        "Raise your mugs, Vikings. Like, raid, share, and bring another Beer Raider aboard!\n\n"
        "🍺 Brew. Farm. Raid."
    )
