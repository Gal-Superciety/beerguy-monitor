import aiohttp
from config import settings
async def token_pairs(mint=None):
    if not (mint or settings.token_mint): return []
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f'https://api.dexscreener.com/latest/dex/tokens/{mint or settings.token_mint}', timeout=15) as r:
                return (await r.json()).get('pairs') or []
    except Exception: return []
async def primary_pair(mint=None):
    pairs = await token_pairs(mint)
    return max(pairs, key=lambda p: float((p.get('liquidity') or {}).get('usd') or 0), default=None)
