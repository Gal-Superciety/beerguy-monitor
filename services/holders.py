from chain.birdeye import token_overview
async def holders_count():
    data=await token_overview(); d=data.get('data') or {}; return int(d.get('holder') or d.get('holders') or 0)
async def holders_text(): return f'👥 <b>Holders</b>\nTotal: {await holders_count():,}'
