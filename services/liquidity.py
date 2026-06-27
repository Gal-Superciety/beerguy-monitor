from services.price import get_price_snapshot
async def liquidity_text():
    s=await get_price_snapshot(); return f'💧 <b>Liquidity</b>\n{s.symbol}: ${s.liquidity_usd:,.0f}'
