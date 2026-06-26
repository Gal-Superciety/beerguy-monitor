"""/test command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from utils.branding import official_links_keyboard, reply_branded_html, with_footer

TEST_TEXT = with_footer("""🍺 <b>BeerGuy Monitor is online!</b>

✅ Telegram connected
✅ Bot is running
✅ Community command system ready""")


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a Telegram connectivity test message."""
    if update.effective_message:
        await reply_branded_html(update.effective_message, TEST_TEXT, reply_markup=official_links_keyboard())
