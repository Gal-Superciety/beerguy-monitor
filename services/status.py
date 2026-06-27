from config import settings
async def status_text():
    return f'✅ <b>BeerGuy Monitor Online</b>\nToken: {settings.token_symbol}\nMint: <code>{settings.token_mint or "not configured"}</code>\nPrivate alerts: {settings.enable_private_alerts}\nGroup alerts: {settings.enable_group_alerts}'
