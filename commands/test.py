"""/test command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

TEST_TEXT = """🍺 BeerGuy Monitor is online!

✅ Telegram connected
✅ Bot is running
⚔️ Brew. Farm. Raid."""


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a Telegram connectivity test message."""
    await update.effective_message.reply_text(TEST_TEXT)
