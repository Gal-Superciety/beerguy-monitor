"""Holder-related services for BeerGuy Monitor."""
from __future__ import annotations

from dataclasses import dataclass

from services.solana import SolanaClient


@dataclass(frozen=True)
class HolderStats:
    """Basic holder and supply summary."""

    largest_accounts: int
    supply: float


class HolderService:
    """Fetch holder-oriented Solana token data."""

    def __init__(self, solana: SolanaClient) -> None:
        self.solana = solana

    async def stats(self) -> HolderStats:
        """Return a lightweight holder summary."""
        accounts, supply = await self.solana.token_largest_accounts(), await self.solana.token_supply()
        return HolderStats(largest_accounts=len(accounts), supply=supply)
