"""DexScreener API client for BeerGuy market data."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

LOGGER = logging.getLogger(__name__)


class DexScreenerClient:
    """Small async client for token and pair data from DexScreener."""

    BASE_URL = "https://api.dexscreener.com/latest/dex"

    def __init__(self, token_mint: str, api_url: str = "") -> None:
        self.token_mint = token_mint
        self.api_url = api_url

    async def get_pairs(self) -> list[dict[str, Any]]:
        """Return all Solana pairs known for the configured token mint."""
        url = self.api_url or f"{self.BASE_URL}/tokens/{self.token_mint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as response:
                response.raise_for_status()
                payload = await response.json()
        pairs = payload.get("pairs") or []
        return [pair for pair in pairs if pair.get("chainId") == "solana"]

    async def get_primary_pair(self) -> dict[str, Any] | None:
        """Return the most liquid Solana pair, if any."""
        pairs = await self.get_pairs()
        if not pairs:
            LOGGER.warning("DexScreener returned no Solana pairs for %s", self.token_mint)
            return None
        return max(pairs, key=lambda pair: float(pair.get("liquidity", {}).get("usd") or 0))
