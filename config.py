"""Application configuration for BeerGuy Monitor.

Configuration is intentionally environment-driven so the same image can run on
Railway, Render, Docker, or a VPS without code changes.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    solana_rpc: str = os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com")
    token_mint: str = os.getenv("TOKEN_MINT", "7mF2JsRcr5MfeTQKkhMM8dZQSRvkpsnxeM23onzbBtuH")
    dexscreener_url: str = os.getenv("DEXSCREENER_URL", "")
    dexscreener_api_url: str = os.getenv("DEXSCREENER_API_URL", "")
    min_buy_alert: float = _get_float("MIN_BUY_ALERT", 25.0)
    big_buy_alert: float = _get_float("BIG_BUY_ALERT", 500.0)
    poll_interval: int = _get_int("POLL_INTERVAL", 20)
    greeting_user_cooldown_seconds: int = _get_int("GREETING_USER_COOLDOWN_SECONDS", 600)
    greeting_group_cooldown_seconds: int = _get_int("GREETING_GROUP_COOLDOWN_SECONDS", 120)
    buy_image: str = os.getenv("BUY_IMAGE", "buy.png")
    sell_image: str = os.getenv("SELL_IMAGE", "sell.png")
    big_buy_image: str = os.getenv("BIG_BUY_IMAGE", "big_buy.png")
    big_sell_image: str = os.getenv("BIG_SELL_IMAGE", "big_sell.png")
    liquidity_image: str = os.getenv("LIQUIDITY_IMAGE", "liquidity.png")
    new_holder_image: str = os.getenv("NEW_HOLDER_IMAGE", "new_holder.png")
    announcement_image: str = os.getenv("ANNOUNCEMENT_IMAGE", "announcement.png")
    giveaway_image: str = os.getenv("GIVEAWAY_IMAGE", "giveaway.png")
    contest_image: str = os.getenv("CONTEST_IMAGE", "contest.png")
    loading_image: str = os.getenv("LOADING_IMAGE", "loading.png")
    logo_image: str = os.getenv("LOGO_IMAGE", "logo.png")
    whale_image: str = os.getenv("WHALE_IMAGE", "whale.png")
    burn_image: str = os.getenv("BURN_IMAGE", "burn.png")
    price_milestone_image: str = os.getenv("PRICE_MILESTONE_IMAGE", "price_milestone.png")
    holder_milestone_image: str = os.getenv("HOLDER_MILESTONE_IMAGE", "holder_milestone.png")

    def validate(self) -> None:
        """Validate settings required to run the Telegram bot."""
        missing = [
            name
            for name, value in {
                "TELEGRAM_TOKEN": self.telegram_token,
                "TELEGRAM_CHAT_ID": self.telegram_chat_id,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


settings = Settings()
