"""/info and /help command handlers."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from utils.branding import BEERGUY_COLORS, official_links_keyboard, reply_branded_html, with_footer

HELP_TEXT = with_footer("""🍺 <b>BeerGuy Monitor Commands</b>

📊 <b>Market</b>
/price - Latest BeerGuy price
/chart - Live chart
/holders - Holder and supply summary
/contract - Full BGUY token information

🍺 <b>Community</b>
/raid - Rally the Beer Raiders
/info - About BeerGuy Monitor

🛠 <b>Utility</b>
/help - Show commands
/test - Confirm Telegram connectivity""")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send organized command help."""
    if update.effective_message:
        await reply_branded_html(update.effective_message, HELP_TEXT, reply_markup=official_links_keyboard())


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send project information."""
    if update.effective_message:
        await reply_branded_html(
            update.effective_message,
            with_footer(
                "🍺 <b>BeerGuy Monitor</b> is the official community bot for BGUY on Solana.\n\n"
                "It serves the Beer Raiders with market snapshots, token information, holder tracking, raid coordination, and production-ready alert modules.\n\n"
                f"🎨 <b>Brand:</b> {BEERGUY_COLORS}\n"
                "🚀 <b>Roadmap-ready:</b> buys, sells, whales, burns, liquidity, milestones, announcements, raids, admin tools, and multi-language support."
            ),
            reply_markup=official_links_keyboard(),
        )
