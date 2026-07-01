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
WEEKLY_POINT_CAP = 1500
_URL_RE = re.compile(r'https?://|www\.', re.I)
_WORD_RE = re.compile(r'[a-z0-9_]+', re.I)


@dataclass(frozen=True)
class ScoreDecision:
    points: int
    reason: str


class LeaderboardStorage:
    """JSON-backed leaderboard storage, isolated for future DB adapters."""

    def __init__(self, store: JsonStore | None = None, event_store: JsonStore | None = None):
        self.store = store
        self.event_store = event_store

    def _store(self):
        if self.store is None:
            self.store = JsonStore('leaderboard.json', self._empty())
        return self.store

    def _event_store(self):
        if self.event_store is None:
            self.event_store = JsonStore('leaderboard_events.json', self._empty_events())
        return self.event_store

    @staticmethod
    def _empty() -> dict:
        return {'users': {}, 'paused': False, 'last_posted_week': None, 'schema_version': 2}

    @staticmethod
    def _empty_events() -> dict:
        return {'events': [], 'schema_version': 1}

    def read(self) -> dict:
        data = self._store().read()
        if not isinstance(data, dict):
            return self._empty()
        return self.migrate(data)

    def migrate(self, data: dict) -> dict:
        """Upgrade leaderboard shape without erasing score data."""
        data.setdefault('users', {})
        data.setdefault('paused', False)
        data.setdefault('last_posted_week', None)
        data['schema_version'] = 2
        for user in data.get('users', {}).values():
            user['weekly_points'] = max(0, int(user.get('weekly_points', 0) or 0))
            user.pop('daily_points', None)
            user.setdefault('scored_messages', [])
            user.setdefault('last_scored_at', '1970-01-01T00:00:00+00:00')
        return data

    def write(self, data: dict) -> None:
        self._store().write(self.migrate(data))

    def read_events(self) -> dict:
        data = self._event_store().read()
        if not isinstance(data, dict):
            data = self._empty_events()
        data.setdefault('events', [])
        data.setdefault('schema_version', 1)
        return data

    def append_event(self, event: dict) -> None:
        data = self.read_events()
        data['events'].append(event)
        self._event_store().write(data)


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

    def reset_week(self, data: dict, week_key: str | None = None) -> None:
        key = week_key or self.week_key()
        for user in data.get('users', {}).values():
            user['weekly_points'] = 0
            user.pop('daily_points', None)
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
        user_id = str(user.id)
        record = data['users'].setdefault(user_id, self._new_user(user, week))
        self._refresh_user(record, user)
        if not record.get('week_key'):
            record['week_key'] = week
        record.pop('daily_points', None)
        signature = self._message_signature(message)
        if signature and signature in set(record.get('scored_messages', [])[-10:]):
            return 0
        last_at = datetime.fromisoformat(record.get('last_scored_at', '1970-01-01T00:00:00+00:00'))
        if (now - last_at).total_seconds() < settings.leaderboard_message_cooldown_seconds:
            return 0
        current_points = int(record.get('weekly_points', 0) or 0)
        if current_points >= WEEKLY_POINT_CAP:
            return 0
        awarded = min(points, WEEKLY_POINT_CAP - current_points)
        record['weekly_points'] = current_points + awarded
        record['last_scored_at'] = now.isoformat()
        if signature:
            record.setdefault('scored_messages', []).append(signature)
            record['scored_messages'] = record['scored_messages'][-25:]
        self.storage.write(data)
        self._append_activity_event(record, message, awarded, week, now, signature)
        return awarded

    def format_leaderboard(self, limit: int = 10) -> str:
        data = self.storage.read()
        users = [u for u in data.get('users', {}).values() if int(u.get('weekly_points', 0)) > 0]
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

    def rebuild_from_events(self) -> tuple[int, int]:
        data = self.storage.read()
        week = self.week_key()
        existing = data.get('users', {})
        rebuilt: dict[str, dict] = {}
        for event in self.storage.read_events().get('events', []):
            if event.get('week_key') != week:
                continue
            user_id = str(event.get('user_id') or '')
            points = int(event.get('points', 0) or 0)
            if not user_id or points <= 0:
                continue
            record = rebuilt.setdefault(user_id, self._user_from_event(event, existing.get(user_id), week))
            current = int(record.get('weekly_points', 0) or 0)
            record['weekly_points'] = min(WEEKLY_POINT_CAP, current + points)
            if event.get('signature'):
                record.setdefault('scored_messages', []).append(event['signature'])
                record['scored_messages'] = record['scored_messages'][-25:]
            if event.get('scored_at'):
                record['last_scored_at'] = event['scored_at']
        if not rebuilt:
            return 0, 0
        for user_id, record in rebuilt.items():
            existing[user_id] = record
        data['users'] = existing
        self.storage.write(data)
        return len(rebuilt), sum(int(u.get('weekly_points', 0) or 0) for u in rebuilt.values())

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
        return {'id': user.id, 'username': user.username, 'first_name': user.first_name, 'weekly_points': 0, 'week_key': week, 'last_scored_at': '1970-01-01T00:00:00+00:00', 'scored_messages': []}

    @staticmethod
    def _user_from_event(event: dict, existing: dict | None, week: str) -> dict:
        record = dict(existing or {})
        record.update({
            'id': event.get('user_id'),
            'username': event.get('username'),
            'first_name': event.get('first_name'),
            'weekly_points': 0,
            'week_key': week,
            'last_scored_at': '1970-01-01T00:00:00+00:00',
            'scored_messages': [],
        })
        return record

    def _append_activity_event(self, record: dict, message, points: int, week: str, now: datetime, signature: str) -> None:
        self.storage.append_event({
            'scored_at': now.isoformat(),
            'week_key': week,
            'user_id': record.get('id'),
            'username': record.get('username'),
            'first_name': record.get('first_name'),
            'chat_id': getattr(message, 'chat_id', None),
            'message_id': getattr(message, 'message_id', None),
            'points': points,
            'signature': signature,
        })

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


async def leaderboard_rebuild(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin(update, context):
        return
    users, points = leaderboard_service.rebuild_from_events()
    if users == 0:
        await update.effective_message.reply_text('No stored activity events are available for the current week. Existing leaderboard scores were left unchanged.')
        return
    await update.effective_message.reply_text(f'Rebuilt leaderboard from stored activity events for {users} users ({points} points).')


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
