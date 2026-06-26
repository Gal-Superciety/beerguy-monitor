"""/raid command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from utils.branding import official_links_keyboard, reply_branded_html, with_footer


async def raid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Rally the BeerGuy community."""
    if update.effective_message:
        await reply_branded_html(
            update.effective_message,
            with_footer(
                "⚔️ <b>Beer Raid Called</b> ⚔️\n\n"
                "Raise your mugs, Vikings. Like, raid, share, and bring another Beer Raider aboard!\n\n"
                "🍺 Born in the hop fields. Raised by Vikings. Built for the Beer Raiders."
            ),
            reply_markup=official_links_keyboard(),
        )
