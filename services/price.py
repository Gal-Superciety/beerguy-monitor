"""Price service built on top of DexScreener data."""
from __future__ import annotations

from dataclasses import dataclass

from services.dexscreener import DexScreenerClient


@dataclass(frozen=True)
class PriceSnapshot:
    """Normalized price and liquidity data for Telegram commands."""

    symbol: str
    price_usd: float
    liquidity_usd: float
    volume_24h: float
    price_change_24h: float
    chart_url: str


class PriceService:
    """Fetch and normalize BeerGuy price data."""

    def __init__(self, client: DexScreenerClient, fallback_chart_url: str = "") -> None:
        self.client = client
        self.fallback_chart_url = fallback_chart_url

    async def snapshot(self) -> PriceSnapshot | None:
        """Return the latest market snapshot, or None when unavailable."""
        pair = await self.client.get_primary_pair()
        if pair is None:
            return None
        base_token = pair.get("baseToken", {})
        return PriceSnapshot(
            symbol=base_token.get("symbol", "BGUY"),
            price_usd=float(pair.get("priceUsd") or 0),
            liquidity_usd=float(pair.get("liquidity", {}).get("usd") or 0),
            volume_24h=float(pair.get("volume", {}).get("h24") or 0),
            price_change_24h=float(pair.get("priceChange", {}).get("h24") or 0),
            chart_url=pair.get("url") or self.fallback_chart_url,
        )
