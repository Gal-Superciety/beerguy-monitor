import aiohttp
from config import settings
async def enhanced_transactions(signatures: list[str]):
    if not settings.helius_api_key or not signatures: return []
    try:
        url=f'https://api.helius.xyz/v0/transactions/?api-key={settings.helius_api_key}'
        async with aiohttp.ClientSession() as s:
            async with s.post(url, json={'transactions': signatures}, timeout=15) as r: return await r.json()
    except Exception: return []
