"""Token metadata aggregation for BeerGuy Monitor."""
from __future__ import annotations

from dataclasses import dataclass

from services.holders import HolderService
from services.solana import SolanaClient


@dataclass(frozen=True)
class TokenInfo:
    """Display-ready Solana token facts."""

    decimals: int | None
    supply: float | None
    holder_count: int | None
    mint_authority: str | None
    freeze_authority: str | None
    metadata: str | None


class TokenInfoService:
    """Fetch token facts from Solana with graceful fallbacks."""

    def __init__(self, solana: SolanaClient, holders: HolderService) -> None:
        self.solana = solana
        self.holders = holders

    async def info(self) -> TokenInfo:
        """Return token mint, supply, and holder information when RPC supports it."""
        account = await self.solana.parsed_account_info()
        parsed_info = (
            account.get("value", {})
            .get("data", {})
            .get("parsed", {})
            .get("info", {})
            if account
            else {}
        )
        supply = await self.solana.token_supply()
        holder_stats = await self.holders.stats()
        return TokenInfo(
            decimals=parsed_info.get("decimals"),
            supply=supply,
            holder_count=holder_stats.holder_count or holder_stats.largest_accounts,
            mint_authority=parsed_info.get("mintAuthority"),
            freeze_authority=parsed_info.get("freezeAuthority"),
            metadata=parsed_info.get("extensions") or parsed_info.get("metadata"),
        )
