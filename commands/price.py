"""/price command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from services.price import PriceService
from utils.branding import official_links_keyboard, reply_branded_html, with_footer
from utils.formatters import format_number


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the latest BeerGuy market snapshot."""
    service: PriceService = context.application.bot_data["price_service"]
    snapshot = await service.snapshot()
    if update.effective_message is None:
        return
    if snapshot is None:
        await reply_branded_html(update.effective_message, with_footer("🍺 Price data is brewing. Try again soon!"), reply_markup=official_links_keyboard())
        return
    await reply_branded_html(
        update.effective_message,
        with_footer(
            "🍺 <b>BeerGuy Price</b> 🍺\n\n"
            f"🪙 {snapshot.symbol}: ${format_number(snapshot.price_usd, 8)}\n"
            f"📊 24h: {format_number(snapshot.price_change_24h, 2)}%\n"
            f"💧 Liquidity: ${format_number(snapshot.liquidity_usd, 2)}\n"
            f"📦 Volume 24h: ${format_number(snapshot.volume_24h, 2)}"
        ),
        reply_markup=official_links_keyboard(),
    )
