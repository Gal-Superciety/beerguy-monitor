from dataclasses import dataclass
from config import settings
from chain.dexscreener import primary_pair
@dataclass(frozen=True)
class PriceSnapshot:
    symbol: str; price_usd: float; liquidity_usd: float; volume_24h: float; price_change_24h: float; chart_url: str
async def get_price_snapshot() -> PriceSnapshot:
    pair = await primary_pair()
    if not pair: return PriceSnapshot(settings.token_symbol, 0, 0, 0, 0, settings.chart_url)
    return PriceSnapshot((pair.get('baseToken') or {}).get('symbol') or settings.token_symbol, float(pair.get('priceUsd') or 0), float((pair.get('liquidity') or {}).get('usd') or 0), float((pair.get('volume') or {}).get('h24') or 0), float((pair.get('priceChange') or {}).get('h24') or 0), pair.get('url') or settings.chart_url)
async def price_text() -> str:
    s = await get_price_snapshot()
    return f'🍺 <b>{s.symbol} Price</b>\nPrice: ${s.price_usd:.8f}\nLiquidity: ${s.liquidity_usd:,.0f}\n24h Volume: ${s.volume_24h:,.0f}\n24h Change: {s.price_change_24h:.2f}%\nChart: {s.chart_url or "N/A"}'
