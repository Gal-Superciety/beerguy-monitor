"""Minimal async Solana JSON-RPC client used by BeerGuy Monitor."""
from __future__ import annotations

from typing import Any

import aiohttp


class SolanaClient:
    """JSON-RPC wrapper for token signatures, parsed transactions, and holders."""

    def __init__(self, rpc_url: str, token_mint: str) -> None:
        self.rpc_url = rpc_url
        self.token_mint = token_mint

    async def _rpc(self, method: str, params: list[Any]) -> Any:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        async with aiohttp.ClientSession() as session:
            async with session.post(self.rpc_url, json=payload, timeout=20) as response:
                response.raise_for_status()
                data = await response.json()
        if "error" in data:
            raise RuntimeError(f"Solana RPC error for {method}: {data['error']}")
        return data.get("result")

    async def signatures(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return recent signatures involving the token mint account."""
        return await self._rpc("getSignaturesForAddress", [self.token_mint, {"limit": limit}])

    async def parsed_transaction(self, signature: str) -> dict[str, Any] | None:
        """Return a parsed transaction for a signature."""
        return await self._rpc(
            "getTransaction",
            [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}],
        )

    async def token_largest_accounts(self) -> list[dict[str, Any]]:
        """Return largest token accounts for holder estimates."""
        result = await self._rpc("getTokenLargestAccounts", [self.token_mint])
        return result.get("value", []) if result else []

    async def token_supply(self) -> float:
        """Return current token supply as a UI amount."""
        result = await self._rpc("getTokenSupply", [self.token_mint])
        return float(result.get("value", {}).get("uiAmount") or 0) if result else 0

    async def parsed_account_info(self) -> dict[str, Any] | None:
        """Return parsed mint account information."""
        return await self._rpc("getAccountInfo", [self.token_mint, {"encoding": "jsonParsed"}])

    async def token_holder_count(self) -> int | None:
        """Best-effort count of non-empty token accounts for the configured mint."""
        filters = [
            {"dataSize": 165},
            {"memcmp": {"offset": 0, "bytes": self.token_mint}},
        ]
        result = await self._rpc(
            "getProgramAccounts",
            [
                "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                {"encoding": "jsonParsed", "filters": filters},
            ],
        )
        if result is None:
            return None
        holders = {
            account.get("account", {})
            .get("data", {})
            .get("parsed", {})
            .get("info", {})
            .get("owner")
            for account in result
            if float(
                account.get("account", {})
                .get("data", {})
                .get("parsed", {})
                .get("info", {})
                .get("tokenAmount", {})
                .get("uiAmount")
                or 0
            ) > 0
        }
        holders.discard(None)
        return len(holders)
