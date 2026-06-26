"""/holders command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from services.holders import HolderService
from utils.branding import official_links_keyboard, reply_branded_html, with_footer
from utils.formatters import format_number


async def holders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send holder and supply information."""
    service: HolderService = context.application.bot_data["holder_service"]
    stats = await service.stats()
    holder_line = stats.holder_count if stats.holder_count is not None else f"Top {stats.largest_accounts} tracked accounts"
    if update.effective_message:
        await reply_branded_html(
            update.effective_message,
            with_footer(
                "🍺 <b>BeerGuy Holders</b>\n\n"
                f"👥 Current Holders: {holder_line}\n"
                f"🪙 Supply: {format_number(stats.supply, 2)} BGUY"
            ),
            reply_markup=official_links_keyboard(),
        )
