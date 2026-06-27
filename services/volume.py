from services.price import get_price_snapshot
async def volume_text():
    s=await get_price_snapshot(); return f'📊 <b>24h Volume</b>\n${s.volume_24h:,.0f}'
