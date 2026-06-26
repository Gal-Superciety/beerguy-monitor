"""/price command handler."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from services.price import PriceService
from utils.formatters import format_number


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the latest BeerGuy market snapshot."""
    service: PriceService = context.application.bot_data["price_service"]
    snapshot = await service.snapshot()
    if snapshot is None:
        await update.effective_message.reply_text("🍺 Price data is brewing. Try again soon!")
        return
    await update.effective_message.reply_html(
        "🍺 <b>BEERGUY PRICE</b> 🍺\n\n"
        f"🪙 {snapshot.symbol}: ${format_number(snapshot.price_usd, 8)}\n"
        f"📊 24h: {format_number(snapshot.price_change_24h, 2)}%\n"
        f"💧 Liquidity: ${format_number(snapshot.liquidity_usd, 2)}\n"
        f"📦 Volume 24h: ${format_number(snapshot.volume_24h, 2)}\n\n"
        "⚔️ Brew. Farm. Raid."
    )
