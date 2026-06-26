"""/info and /help command handlers."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = """🍺 BEERGUY MONITOR 🍺

Commands:
/price - Latest BeerGuy price
/chart - DexScreener chart
/contract - BGUY mint address
/holders - Holder and supply summary
/raid - Rally the Beer Raiders
/test - Confirm Telegram connectivity
/help - Show commands
/info - About BeerGuy Monitor

⚔️ Brew. Farm. Raid."""


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send command help."""
    await update.effective_message.reply_text(HELP_TEXT)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send project information."""
    await update.effective_message.reply_text(
        "🍺 BeerGuy Monitor is the official community bot for tracking BGUY activity on Solana.\n\n"
        "Built for buy alerts, holder alerts, price checks, raid coordination, and future BeerGuy ecosystem automation.\n\n"
        "⚔️ Brew. Farm. Raid."
    )
