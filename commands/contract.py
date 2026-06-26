"""/contract command handler."""
from __future__ import annotations

from html import escape

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from services.token import TokenInfoService
from utils.branding import (
    BEERGUY_CREATED,
    BEERGUY_MINT,
    BEERGUY_NETWORK,
    BEERGUY_TICKER,
    official_links_keyboard,
    reply_branded_html,
    with_footer,
)
from utils.formatters import format_number, solscan_token_url


def _value(value: object) -> str:
    if value in (None, "", []):
        return "Unavailable"
    text = str(value)
    if len(text) > 240:
        text = f"{text[:237]}..."
    return escape(text)


async def contract_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send full BeerGuy token information."""
    message = update.effective_message
    if message is None:
        return
    token_mint = settings.token_mint or BEERGUY_MINT
    service: TokenInfoService = context.application.bot_data["token_info_service"]
    try:
        info = await service.info()
    except Exception:
        info = None

    holders = _value(info.holder_count if info else None)
    decimals = _value(info.decimals if info else None)
    supply = format_number(info.supply, 2) if info and info.supply is not None else "Unavailable"
    mint_authority = _value(info.mint_authority if info else None)
    freeze_authority = _value(info.freeze_authority if info else None)
    metadata = _value(info.metadata if info else None)

    await reply_branded_html(
        message,
        with_footer(
            "🍺 <b>BeerGuy Token Information</b>\n\n"
            "<b>Token Name:</b> BeerGuy\n"
            f"<b>Ticker:</b> {BEERGUY_TICKER}\n"
            f"<b>Network:</b> {BEERGUY_NETWORK}\n"
            f"<b>Mint Address:</b>\n<code>{token_mint}</code>\n"
            f"<b>Created:</b> {BEERGUY_CREATED}\n\n"
            f"👥 <b>Current Holders:</b> {holders}\n"
            f"🔢 <b>Decimals:</b> {decimals}\n"
            f"🪙 <b>Total Supply:</b> {supply} {BEERGUY_TICKER}\n"
            f"🛡 <b>Mint Authority:</b> <code>{mint_authority}</code>\n"
            f"❄️ <b>Freeze Authority:</b> <code>{freeze_authority}</code>\n"
            f"🧾 <b>Metadata:</b> {metadata}\n"
            "🖼 <b>Token Logo:</b> included when the production logo asset is available.\n\n"
            f"🔎 <a href=\"{solscan_token_url(token_mint)}\">View on Solscan</a>"
        ),
        reply_markup=official_links_keyboard(),
    )
