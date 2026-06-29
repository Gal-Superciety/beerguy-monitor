import logging
from pathlib import Path
from typing import Awaitable, Callable

from telegram import Bot

from config import settings
from storage.files import image_path

logger = logging.getLogger(__name__)

PhotoSender = Callable[[object], Awaitable[object]]
TextSender = Callable[[str], Awaitable[object]]


def _photo_available(path: Path | None) -> bool:
    return path is not None and path.exists() and path.is_file() and path.stat().st_size > 0


async def send_optional_photo(
    photo_path: Path | None,
    text: str,
    send_photo: PhotoSender,
    send_text: TextSender,
    *,
    fallback_log: str | None = None,
):
    """Send a photo when available, otherwise fall back to text only."""
    try:
        if _photo_available(photo_path):
            with photo_path.open('rb') as photo:
                return await send_photo(photo)
    except OSError:
        # Treat missing/unreadable assets as optional so bot commands keep working.
        pass

    if fallback_log:
        logger.warning(fallback_log)
    return await send_text(text)


async def send_with_optional_image(bot: Bot, chat_id: str | int, text: str, image_kind: str | None = None):
    path = image_path(image_kind) if image_kind else None

    async def send_photo(photo):
        return await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode='HTML')

    async def send_text(message: str):
        return await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML', disable_web_page_preview=True)

    return await send_optional_photo(path, text, send_photo, send_text)


async def broadcast_alert(bot: Bot, text: str, image_kind: str):
    if settings.enable_private_alerts and settings.telegram_private_chat_id:
        await send_with_optional_image(bot, settings.telegram_private_chat_id, text, image_kind)
    if settings.enable_group_alerts and settings.telegram_group_chat_id:
        await send_with_optional_image(bot, settings.telegram_group_chat_id, text, image_kind)
