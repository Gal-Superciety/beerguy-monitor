import asyncio
import services.price as price

def test_price_fallback(monkeypatch):
    async def none(): return None
    monkeypatch.setattr(price, 'primary_pair', none)
    snap = asyncio.run(price.get_price_snapshot())
    assert snap.symbol == 'BGUY'
    assert snap.price_usd == 0
