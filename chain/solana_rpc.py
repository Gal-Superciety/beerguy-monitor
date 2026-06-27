import aiohttp
from config import settings
async def rpc_call(method: str, params=None):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(settings.solana_rpc_url, json={'jsonrpc':'2.0','id':1,'method':method,'params':params or []}, timeout=15) as r:
                data = await r.json(); return data.get('result')
    except Exception: return None
async def get_token_supply(mint: str | None = None): return await rpc_call('getTokenSupply', [mint or settings.token_mint]) if (mint or settings.token_mint) else None
