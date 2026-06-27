from __future__ import annotations
from enum import Enum
class TxType(str, Enum):
    BUY='BUY'; SELL='SELL'; LIQUIDITY_ADD='LIQUIDITY_ADD'; LIQUIDITY_REMOVE='LIQUIDITY_REMOVE'; TRANSFER='TRANSFER'
def classify_transaction(tx: dict, token_mint: str='', quote_mint: str='') -> TxType:
    text = str(tx).lower()
    if 'liquidity' in text and any(w in text for w in ('add','increase','deposit')): return TxType.LIQUIDITY_ADD
    if 'liquidity' in text and any(w in text for w in ('remove','decrease','withdraw')): return TxType.LIQUIDITY_REMOVE
    if 'buy' in text: return TxType.BUY
    if 'sell' in text: return TxType.SELL
    token_delta = float(tx.get('token_delta', tx.get('base_delta', 0)) or 0)
    quote_delta = float(tx.get('quote_delta', 0) or 0)
    if token_delta > 0 and quote_delta < 0: return TxType.BUY
    if token_delta < 0 and quote_delta > 0: return TxType.SELL
    return TxType.TRANSFER
