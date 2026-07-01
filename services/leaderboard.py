from __future__ import annotations

import json
import logging
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes

from config import settings
from storage.json_store import JsonStore
from utils.spam_detector import SpamDetector

logger = logging.getLogger(__name__)

BEER_KEYWORDS = {
    'beer', 'beerguy', 'bguy', 'brew', 'brewing', 'farm', 'farming', 'raid', 'raiding',
    'raider', 'raiders', 'cheers', 'chart', 'buy', 'holder', 'holders', 'liquidity',
    'sol', 'solana', 'token', 'ca', 'contract', 'dex', 'bullish', 'tavern',
}
SHORT_LOW_VALUE = {'ok', 'okay', 'lol', 'lmao', 'rofl', 'haha', 'hehe', '.', '..', '...', 'gm', 'hi', 'hey', 'yo'}
DAY_NAMES = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
_URL_RE = re.compile(r'https?://|www\.', re.I)
_WORD_RE = re.compile(r'[a-z0-9_]+', re.I)


@dataclass(frozen=True)
class ScoreDecision:
    points: int
    reason: str


class LeaderboardStorage:
    """JSON-backed leaderboard storage, isolated for future DB adapters."""

    def __init__(self, store: JsonStore | None = None):
        self.store = store

    def _store(self):
        if self.store is None:
            self.store = JsonStore('leaderboard.json', self._empty())
        return self.store

    @staticmethod
    def _empty() -> dict:
        return {'users': {}, 'paused': False, 'last_posted_week': None}

    def read(self) -> dict:
        data = self._store().read()
        if not isinstance(data, dict):
            return self._empty()
        data.setdefault('users', {})
        data.setdefault('paused', False)
        data.setdefault('last_posted_week', None)
        return data

    def write(self, data: dict) -> None:
        self._store().write(data)


class LeaderboardService:
    def __init__(self, storage: LeaderboardStorage | None = None):
        self.storage = storage or LeaderboardStorage()
        self.detector = SpamDetector()

    def timezone(self) -> ZoneInfo:
        try:
            return ZoneInfo(settings.leaderboard_timezone)
        except ZoneInfoNotFoundError:
            logger.warning('Invalid LEADERBOARD_TIMEZONE=%s; using UTC', settings.leaderboard_timezone)
            return ZoneInfo('UTC')

    def now(self) -> datetime:
        return datetime.now(self.timezone())

    def week_key(self, dt: datetime | None = None) -> str:
        current = dt or self.now()
        year, week, _ = current.isocalendar()
        return f'{year}-W{week:02d}'

    def day_key(self, dt: datetime | None = None) -> str:
        return (dt or self.now()).strftime('%Y-%m-%d')

    def reset_week(self, data: dict, week_key: str | None = None) -> None:
        key = week_key or self.week_key()
        for user in data.get('users', {}).values():
            user['weekly_points'] = 0
            user['daily_points'] = {}
            user['scored_messages'] = []
            user['week_key'] = key

    def score_message(self, update: Update) -> ScoreDecision:
        message = update.effective_message
        user = update.effective_user
        if not message or not user or user.is_bot:
            return ScoreDecision(0, 'bot_or_missing')
        text = (message.text or message.caption or '').strip()
        has_media = bool(message.photo or message.animation or message.video or message.sticker or message.document)
        if not text and not has_media:
            return ScoreDecision(0, 'empty')
        normalized = self._normalize(text)
        if normalized in SHORT_LOW_VALUE:
            return ScoreDecision(0, 'too_short')
        if text and len(text) < 4 and not has_media:
            return ScoreDecision(0, 'too_short')
        if _URL_RE.search(text) and self.detector.check(message.chat_id, user.id, text).is_spam:
            return ScoreDecision(0, 'spam_link')
        points = 0
        if text:
            points += 1
        if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id != user.id:
            points += 2
        if self._is_useful_beerguy_message(text):
            points += 3
        if has_media:
            points += 2
        return ScoreDecision(points, 'scored' if points else 'no_score')

    def score_invites(self, update: Update) -> int:
        message = update.effective_message
        inviter = update.effective_user
        if not message or not inviter or inviter.is_bot or not message.new_chat_members:
            return 0
        count = sum(1 for member in message.new_chat_members if not member.is_bot and member.id != inviter.id)
        return count * 5

    def record_activity(self, update: Update) -> int:
        if not settings.leaderboard_enabled:
            return 0
        data = self.storage.read()
        if data.get('paused'):
            return 0
        points = self.score_invites(update) if update.effective_message and update.effective_message.new_chat_members else self.score_message(update).points
        if points <= 0:
            return 0
        user = update.effective_user
        message = update.effective_message
        if not user or not message:
            return 0
        now = self.now()
        week = self.week_key(now)
        day = self.day_key(now)
        user_id = str(user.id)
        record = data['users'].setdefault(user_id, self._new_user(user, week))
        self._refresh_user(record, user)
        if record.get('week_key') != week:
            record['weekly_points'] = 0
            record['daily_points'] = {}
            record['scored_messages'] = []
            record['week_key'] = week
        signature = self._message_signature(message)
        if signature and signature in set(record.get('scored_messages', [])[-10:]):
            return 0
        last_at = datetime.fromisoformat(record.get('last_scored_at', '1970-01-01T00:00:00+00:00'))
        if (now - last_at).total_seconds() < settings.leaderboard_message_cooldown_seconds:
            return 0
        daily_points = int(record.get('daily_points', {}).get(day, 0))
        allowed = max(settings.leaderboard_max_daily_points - daily_points, 0)
        awarded = min(points, allowed)
        if awarded <= 0:
            return 0
        record['weekly_points'] = int(record.get('weekly_points', 0)) + awarded
        record.setdefault('daily_points', {})[day] = daily_points + awarded
        record['last_scored_at'] = now.isoformat()
        if signature:
            record.setdefault('scored_messages', []).append(signature)
            record['scored_messages'] = record['scored_messages'][-25:]
        self.storage.write(data)
        return awarded

    def format_leaderboard(self, limit: int = 10) -> str:
        data = self.storage.read()
        week = self.week_key()
        users = [u for u in data.get('users', {}).values() if u.get('week_key') == week and int(u.get('weekly_points', 0)) > 0]
        users.sort(key=lambda u: int(u.get('weekly_points', 0)), reverse=True)
        lines = ['🏆 <b>Weekly Beer Raiders Leaderboard</b>', '']
        medals = ['🥇', '🥈', '🥉']
        if not users:
            lines.append('No scored raids yet this week. Start brewing the chat! 🍺')
        for idx, user in enumerate(users[:limit], start=1):
            icon = medals[idx - 1] if idx <= 3 else f'{idx}.'
            lines.append(f'{icon} {self._display_name(user)} — {int(user.get("weekly_points", 0))} points')
        lines.extend(['', '⚔️ Brew. Farm. Raid.'])
        return '\n'.join(lines)

    def export_json(self) -> str:
        return json.dumps(self.storage.read(), indent=2, sort_keys=True)

    def set_paused(self, paused: bool) -> None:
        data = self.storage.read(); data['paused'] = paused; self.storage.write(data)

    def reset_current_week(self) -> None:
        data = self.storage.read(); self.reset_week(data); self.storage.write(data)

    async def maybe_post_weekly_report(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not settings.leaderboard_enabled or not settings.telegram_group_chat_id:
            return
        data = self.storage.read()
        if data.get('paused'):
            return
        week = self.week_key()
        if data.get('last_posted_week') == week:
            return
        await context.bot.send_message(settings.telegram_group_chat_id, self.format_leaderboard(), parse_mode='HTML')
        data = self.storage.read()
        data['last_posted_week'] = week
        self.reset_week(data, self.week_key())
        self.storage.write(data)

    def next_report_time(self) -> datetime:
        now = self.now()
        target_day = DAY_NAMES.get(settings.leaderboard_post_day.strip().lower(), 5)
        days = (target_day - now.weekday()) % 7
        target = now.replace(hour=settings.leaderboard_post_hour, minute=0, second=0, microsecond=0) + timedelta(days=days)
        if target <= now:
            target += timedelta(days=7)
        return target

    @staticmethod
    def _normalize(text: str) -> str:
        return ' '.join(_WORD_RE.findall(text.casefold()))

    @classmethod
    def _is_useful_beerguy_message(cls, text: str) -> bool:
        normalized = cls._normalize(text)
        words = set(normalized.split())
        return len(normalized) >= 20 and bool(words & BEER_KEYWORDS)

    @classmethod
    def _message_signature(cls, message) -> str:
        text = cls._normalize(message.text or message.caption or '')
        if text:
            return text[:160]
        if message.photo:
            return f'photo:{message.photo[-1].file_unique_id}'
        if message.animation:
            return f'animation:{message.animation.file_unique_id}'
        if message.sticker:
            return f'sticker:{message.sticker.file_unique_id}'
        return ''

    @staticmethod
    def _new_user(user, week: str) -> dict:
        return {'id': user.id, 'username': user.username, 'first_name': user.first_name, 'weekly_points': 0, 'daily_points': {}, 'week_key': week, 'last_scored_at': '1970-01-01T00:00:00+00:00', 'scored_messages': []}

    @staticmethod
    def _refresh_user(record: dict, user) -> None:
        record['username'] = user.username
        record['first_name'] = user.first_name

    @staticmethod
    def _display_name(user: dict) -> str:
        if user.get('username'):
            return f'@{user["username"]}'
        return user.get('first_name') or f'Raider {user.get("id")}'


leaderboard_service = LeaderboardService()


async def handle_leaderboard_activity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    leaderboard_service.record_activity(update)


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not settings.leaderboard_enabled:
        await update.effective_message.reply_text('Leaderboard is currently disabled.')
        return
    await update.effective_message.reply_html(leaderboard_service.format_leaderboard())


async def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    if not user:
        return False
    if settings.admin_telegram_id and user.id == settings.admin_telegram_id:
        return True
    if not chat:
        return False
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
    except Exception:
        return False
    return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}


async def require_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if await _is_admin(update, context):
        return True
    await update.effective_message.reply_text('Admin only.')
    return False


async def leaderboard_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin(update, context):
        return
    leaderboard_service.reset_current_week()
    await update.effective_message.reply_text('Weekly leaderboard has been reset.')


async def leaderboard_pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin(update, context):
        return
    leaderboard_service.set_paused(True)
    await update.effective_message.reply_text('Leaderboard scoring is paused.')


async def leaderboard_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin(update, context):
        return
    leaderboard_service.set_paused(False)
    await update.effective_message.reply_text('Leaderboard scoring is resumed.')


async def leaderboard_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin(update, context):
        return
    payload = leaderboard_service.export_json().encode('utf-8')
    with tempfile.NamedTemporaryFile('wb', suffix='.json', delete=False) as tmp:
        tmp.write(payload)
        path = Path(tmp.name)
    try:
        with path.open('rb') as export_file:
            await update.effective_message.reply_document(document=export_file, filename='beerguy_leaderboard_export.json')
    finally:
        path.unlink(missing_ok=True)


def schedule_weekly_report(application) -> None:
    if not settings.leaderboard_enabled:
        return
    if not application.job_queue:
        logger.warning('Leaderboard weekly reports require python-telegram-bot[job-queue]; automatic posting disabled')
        return
    first = leaderboard_service.next_report_time()
    application.job_queue.run_repeating(leaderboard_service.maybe_post_weekly_report, interval=timedelta(days=7), first=first, name='weekly_leaderboard_report')
