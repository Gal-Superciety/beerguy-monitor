from telegram import Bot
from config import settings
from storage.files import image_path
async def send_with_optional_image(bot: Bot, chat_id: str|int, text: str, image_kind: str|None=None):
    path = image_path(image_kind) if image_kind else None
    if path:
        with path.open('rb') as photo: return await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode='HTML')
    return await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML', disable_web_page_preview=True)
async def broadcast_alert(bot: Bot, text: str, image_kind: str):
    if settings.enable_private_alerts and settings.telegram_private_chat_id: await send_with_optional_image(bot, settings.telegram_private_chat_id, text, image_kind)
    if settings.enable_group_alerts and settings.telegram_group_chat_id: await send_with_optional_image(bot, settings.telegram_group_chat_id, text, image_kind)
