"""Official BeerGuy links command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from services.community import LINKS_TEXT
from utils.branding import reply_branded_html
from utils.keyboards import official_links_keyboard


async def links_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send official BeerGuy community links."""
    if update.effective_message:
        await reply_branded_html(
            update.effective_message,
            LINKS_TEXT,
            reply_markup=official_links_keyboard(include_contract_callback=False),
        )
