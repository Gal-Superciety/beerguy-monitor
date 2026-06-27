from dataclasses import dataclass
from config import settings
@dataclass(frozen=True)
class PoolConfig:
    token_mint: str = settings.token_mint
    quote_mint: str = settings.quote_mint
    token_symbol: str = settings.token_symbol
    quote_symbol: str = settings.quote_symbol
DEFAULT_POOL = PoolConfig()
