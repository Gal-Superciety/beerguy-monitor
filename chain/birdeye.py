import aiohttp
from config import settings
async def _get(path, params):
    if not settings.birdeye_api_key: return {}
    try:
        async with aiohttp.ClientSession(headers={'X-API-KEY':settings.birdeye_api_key,'x-chain':'solana'}) as s:
            async with s.get('https://public-api.birdeye.so'+path, params=params, timeout=15) as r: return await r.json()
    except Exception: return {}
async def token_price(mint=None): return await _get('/defi/price', {'address': mint or settings.token_mint})
async def token_overview(mint=None): return await _get('/defi/token_overview', {'address': mint or settings.token_mint})
