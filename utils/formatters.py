"""Formatting helpers for BeerGuy Monitor messages and links."""
from __future__ import annotations


def shorten_wallet(wallet: str, head: int = 3, tail: int = 3) -> str:
    """Return a compact wallet address suitable for Telegram alerts."""
    if not wallet or len(wallet) <= head + tail + 3:
        return wallet
    return f"{wallet[:head]}...{wallet[-tail:]}"


def format_number(value: float, maximum_fraction_digits: int = 2) -> str:
    """Format a number with thousands separators and trimmed decimals."""
    formatted = f"{value:,.{maximum_fraction_digits}f}"
    return formatted.rstrip("0").rstrip(".")


def solscan_tx_url(signature: str) -> str:
    """Build a Solscan transaction URL."""
    return f"https://solscan.io/tx/{signature}"


def solscan_account_url(address: str) -> str:
    """Build a Solscan account URL."""
    return f"https://solscan.io/account/{address}"
