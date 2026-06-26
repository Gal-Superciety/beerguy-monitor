"""Alert detection and Telegram delivery for BeerGuy Monitor."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from telegram import Bot

from config import Settings
from services.solana import SolanaClient
from utils.formatters import format_number, shorten_wallet, solscan_tx_url
from utils.images import image_path

LOGGER = logging.getLogger(__name__)
LAMPORTS_PER_SOL = 1_000_000_000


@dataclass(frozen=True)
class BuyEvent:
    """Normalized buy event produced from a parsed Solana transaction."""

    signature: str
    buyer: str
    sol_spent: float
    token_received: float
    usd_value: float


class AlertService:
    """Poll Solana transactions and publish BeerGuy buy alerts to Telegram."""

    def __init__(self, bot: Bot, solana: SolanaClient, settings: Settings, token_mint: str | None = None) -> None:
        self.bot = bot
        self.solana = solana
        self.settings = settings
        self.token_mint = token_mint or settings.token_mint
        self.seen_signatures: set[str] = set()
        self.seen_holders: set[str] = set()

    async def run_forever(self) -> None:
        """Continuously poll Solana for alert-worthy transactions."""
        while True:
            try:
                await self.poll_once()
            except Exception:
                LOGGER.exception("Alert polling failed")
            await asyncio.sleep(self.settings.poll_interval)

    async def poll_once(self) -> None:
        """Process recent signatures once."""
        for item in reversed(await self.solana.signatures()):
            signature = item.get("signature")
            if not signature or signature in self.seen_signatures:
                continue
            self.seen_signatures.add(signature)
            transaction = await self.solana.parsed_transaction(signature)
            event = self._extract_buy_event(signature, transaction)
            if event and event.usd_value >= self.settings.min_buy_alert:
                await self.send_buy_alert(event)
                if event.buyer not in self.seen_holders:
                    self.seen_holders.add(event.buyer)
                    await self.send_new_holder_alert(event.buyer)

    def _extract_buy_event(self, signature: str, transaction: dict[str, Any] | None) -> BuyEvent | None:
        """Best-effort buy extraction from token balance and SOL balance deltas."""
        if not transaction or transaction.get("meta", {}).get("err"):
            return None
        meta = transaction.get("meta", {})
        message = transaction.get("transaction", {}).get("message", {})
        account_keys = message.get("accountKeys", [])
        buyer = account_keys[0].get("pubkey") if account_keys and isinstance(account_keys[0], dict) else ""
        pre_balances = meta.get("preBalances", [])
        post_balances = meta.get("postBalances", [])
        sol_spent = 0.0
        if pre_balances and post_balances and pre_balances[0] > post_balances[0]:
            sol_spent = (pre_balances[0] - post_balances[0]) / LAMPORTS_PER_SOL

        pre_token = self._token_amount(meta.get("preTokenBalances", []), buyer)
        post_token = self._token_amount(meta.get("postTokenBalances", []), buyer)
        token_received = max(post_token - pre_token, 0.0)
        if not buyer or token_received <= 0:
            return None
        usd_value = sol_spent * 240.0  # Conservative fallback until a live SOL/USD feed is added.
        return BuyEvent(signature, buyer, sol_spent, token_received, usd_value)

    def _token_amount(self, balances: list[dict[str, Any]], owner: str) -> float:
        for balance in balances:
            if balance.get("mint") == self.token_mint and balance.get("owner") == owner:
                return float(balance.get("uiTokenAmount", {}).get("uiAmount") or 0)
        return 0.0

    async def send_buy_alert(self, event: BuyEvent) -> None:
        """Send a buy or big-buy Telegram alert."""
        is_big = event.usd_value >= self.settings.big_buy_alert
        title = "🚨 BIG BEER RAID 🚨" if is_big else "🍺 BEERGUY BUY ALERT 🍺"
        intro = "The Vikings are loading the longship!" if is_big else "A Beer Raider just filled another barrel!"
        caption = (
            f"{title}\n\n{intro}\n\n"
            f"💰 Buy: {format_number(event.sol_spent, 4)} SOL\n"
            f"🪙 Received: {format_number(event.token_received, 2)} BGUY\n"
            f"💵 Value: ${format_number(event.usd_value, 2)}\n\n"
            f"👤 Wallet:\n{shorten_wallet(event.buyer)}\n\n"
            f"📈 <a href=\"{self.settings.dexscreener_url}\">Chart</a>\n"
            f"🔗 <a href=\"{solscan_tx_url(event.signature)}\">Transaction</a>\n\n"
            "⚔️ Brew. Farm. Raid."
        )
        await self._send_photo_or_message("big_buy.png" if is_big else "buy.png", caption)

    async def send_new_holder_alert(self, wallet: str) -> None:
        """Send a first-seen holder alert."""
        caption = (
            "🍺 NEW BEER RAIDER 🍺\n\n"
            "A new Viking has joined the Beer Raiders!\n\n"
            f"👤 Wallet:\n{shorten_wallet(wallet)}\n\n"
            "🔥 Welcome, Raider!\n\n⚔️ Brew. Farm. Raid."
        )
        await self._send_photo_or_message("new_holder.png", caption)

    async def _send_photo_or_message(self, asset_name: str, caption: str) -> None:
        path = image_path(asset_name)
        if path:
            with path.open("rb") as photo:
                await self.bot.send_photo(self.settings.telegram_chat_id, photo, caption=caption, parse_mode="HTML")
        else:
            await self.bot.send_message(self.settings.telegram_chat_id, caption, parse_mode="HTML", disable_web_page_preview=True)
