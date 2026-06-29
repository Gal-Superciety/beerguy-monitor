from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from telegram import ChatPermissions, Update
from telegram.constants import ChatMemberStatus
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import ApplicationHandlerStop, ContextTypes

from utils.spam_detector import SpamDetector, SpamResult

logger = logging.getLogger(__name__)
_detector = SpamDetector()


def _user_label(update: Update) -> str:
    user = update.effective_user
    if not user:
        return 'unknown user'
    handle = f' @{user.username}' if user.username else ''
    return f'{user.id}{handle}'


async def _can_delete_and_restrict(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple[bool, bool]:
    chat = update.effective_chat
    if not chat:
        return False, False
    try:
        member = await context.bot.get_chat_member(chat.id, context.bot.id)
    except TelegramError as exc:
        logger.warning('Moderation permission check failed in chat %s: %s', chat.id, exc)
        return False, False
    if member.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
        logger.warning('Moderation disabled in chat %s: bot is not an administrator', chat.id)
        return False, False
    can_delete = bool(getattr(member, 'can_delete_messages', False) or member.status == ChatMemberStatus.OWNER)
    can_restrict = bool(getattr(member, 'can_restrict_members', False) or member.status == ChatMemberStatus.OWNER)
    if not can_delete:
        logger.warning('Moderation cannot delete messages in chat %s: missing can_delete_messages permission', chat.id)
    if not can_restrict:
        logger.warning('Moderation cannot restrict users in chat %s: missing can_restrict_members permission', chat.id)
    return can_delete, can_restrict


async def _safe_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    can_delete, _ = await _can_delete_and_restrict(update, context)
    if not can_delete:
        return
    try:
        await message.delete()
        logger.info('Deleted spam message chat=%s message=%s user=%s', message.chat_id, message.message_id, _user_label(update))
    except (BadRequest, Forbidden) as exc:
        logger.warning('Failed to delete spam message chat=%s message=%s: %s', message.chat_id, message.message_id, exc)


async def _safe_warn(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if not chat or not user:
        return
    try:
        await context.bot.send_message(chat.id, f'⚠️ @{user.username or user.first_name}, please avoid spam or suspicious links. BeerGuy keeps the tavern safe. 🍺')
        logger.info('Warned user chat=%s user=%s reason=%s', chat.id, _user_label(update), reason)
    except TelegramError as exc:
        logger.warning('Failed to warn user chat=%s user=%s: %s', chat.id, _user_label(update), exc)


async def _safe_restrict(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if not chat or not user:
        return
    _, can_restrict = await _can_delete_and_restrict(update, context)
    if not can_restrict:
        return
    until_date = update.effective_message.date + timedelta(minutes=30) if update.effective_message and update.effective_message.date else datetime.now(timezone.utc) + timedelta(minutes=30)
    permissions = ChatPermissions(can_send_messages=False)
    try:
        await context.bot.restrict_chat_member(chat.id, user.id, permissions=permissions, until_date=until_date)
        logger.info('Restricted user chat=%s user=%s reason=%s duration=30m', chat.id, _user_label(update), reason)
    except (BadRequest, Forbidden) as exc:
        logger.warning('Failed to restrict user chat=%s user=%s: %s', chat.id, _user_label(update), exc)


async def moderate_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat or user.is_bot:
        return
    text = message.text or message.caption or ''
    if not text:
        return
    result: SpamResult = _detector.check(chat.id, user.id, text)
    if not result.is_spam:
        return
    logger.info('Spam detection event chat=%s message=%s user=%s reason=%s severity=%s', chat.id, message.message_id, _user_label(update), result.reason, result.severity)
    if result.severity == 'high':
        logger.warning('Detected phishing/scam attempt chat=%s user=%s reason=%s text=%r', chat.id, _user_label(update), result.reason, text[:300])
    await _safe_delete(update, context)
    warning_count = _detector.record_warning(chat.id, user.id)
    if warning_count == 1:
        await _safe_warn(update, context, result.reason)
    else:
        await _safe_restrict(update, context, result.reason)
    raise ApplicationHandlerStop
