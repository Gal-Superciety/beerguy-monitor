from __future__ import annotations

import random
import re
import time
import unicodedata
from dataclasses import dataclass, field

from telegram import Update
from telegram.ext import ContextTypes

from bot.alerts import send_with_optional_image
from config import settings

_WORD_RE = re.compile(r'[\wăâîșşțţ]+', re.I)
KEYWORDS = {'beer', 'cheers', 'raid', 'brew', 'farm', 'bguy', 'beerguy'}

GENERAL_GREETINGS = {'hi', 'hello', 'hey', 'salut', 'buna', 'buna ziua'}
MORNING_GREETINGS = {'gm', 'good morning', 'buna dimineata'}
AFTERNOON_GREETINGS = {'good afternoon'}
EVENING_GREETINGS = {'good evening'}
GOOD_NIGHT_GREETINGS = {'noapte buna'}

GENERAL_REPLIES = [
    '🍺 Hey Raider! Welcome to the BeerGuy community!',
    '🍻 Salut! BeerGuy is online and ready to raid.',
    '🍺 Hello, Beer Raider! Pull up a chair and say cheers.',
    '🍻 Bună! Brew. Farm. Raid.',
    '🍺 Welcome aboard! Great to see you in the BeerGuy tavern.',
    '🍻 Hey hey! May your raids be strong and your beer cold.',
    '🍺 Salutare, Raider! The BeerGuy community is brewing.',
]
MORNING_REPLIES = [
    '☀️ Good morning, Beer Raider! Time to brew, farm, and raid.',
    '🍺 GM! Fresh day, fresh raids, fresh BeerGuy energy.',
    '☀️ Bună dimineața! Let’s make it a legendary BeerGuy day.',
    '🍻 GM, Raider! May your morning be bullish and your beer cold.',
    '☀️ Rise and raid! BeerGuy is awake.',
]
AFTERNOON_REPLIES = [
    '🍺 Good afternoon, Raider! Keep brewing and raiding.',
    '🍻 Good afternoon! BeerGuy energy is still flowing.',
    '🍺 Afternoon check-in: Brew. Farm. Raid.',
    '🍻 Hope your afternoon is as strong as a BeerGuy raid.',
    '🍺 Good afternoon! Cheers from the BeerGuy tavern.',
]
EVENING_REPLIES = [
    '🌙 Good evening, Raider! Time to relax with BeerGuy.',
    '🍺 Good evening! The tavern lights are on.',
    '🍻 Evening cheers from BeerGuy. Brew. Farm. Raid.',
    '🌙 Good evening, Beer Raider! Thanks for riding with the community.',
    '🍺 The night is young and BeerGuy is still brewing.',
]
GOOD_NIGHT_REPLIES = [
    '🌙 Noapte bună, Raider! Dream of legendary raids.',
    '🍺 Sleep well, Beer Raider. Tomorrow we brew again.',
    '🌙 Good night! May your next raid be glorious.',
    '🍻 Noapte bună! BeerGuy will keep the tavern warm.',
    '🌙 Rest up, Raider. Brew. Farm. Raid. Repeat.',
]
KEYWORD_REPLIES = [
    '🍺 Cheers, Raider!',
    '🍻 Brew. Farm. Raid.',
    '⚔️ Raid energy detected!',
    '🍺 BeerGuy community is brewing.',
    '🍻 Raise a glass to BGUY!',
    '🚜 Farm strong, raid harder.',
]
WELCOME_REPLIES = [
    '🍺 <b>Welcome to BeerGuy!</b>\n\nWelcome aboard, Beer Raider!\n\nBrew. Farm. Raid.\n\nIntroduce yourself and say hello to the community!',
    '🍻 <b>Welcome to BeerGuy!</b>\n\nA new Raider entered the tavern. Say hello and get ready to brew, farm, and raid!',
    '🍺 <b>Welcome aboard, Beer Raider!</b>\n\nThe BeerGuy community is glad to have you here. Introduce yourself and say cheers!',
    '⚔️ <b>New Raider joined BeerGuy!</b>\n\nGrab a beer, meet the community, and prepare to raid.',
    '🍻 <b>Cheers and welcome!</b>\n\nYou are now part of BeerGuy. Brew. Farm. Raid.',
]
GOODBYE_REPLIES = [
    'Good luck on your journey, Raider! 🍺',
]


def normalize_message(text: str) -> str:
    n = unicodedata.normalize('NFKD', text.casefold())
    n = ''.join(c for c in n if not unicodedata.combining(c))
    return ' '.join(_WORD_RE.findall(n))


@dataclass
class CommunityThrottle:
    global_last_reply_at: float = 0.0
    last_user_id: int | None = None
    user_last_reply_at: dict[int, float] = field(default_factory=dict)

    def can_reply(self, user_id: int, now: float) -> bool:
        cooldown = max(settings.auto_reply_cooldown, 0)
        if self.last_user_id == user_id:
            return False
        if now - self.global_last_reply_at < cooldown:
            return False
        if now - self.user_last_reply_at.get(user_id, 0.0) < cooldown * 3:
            return False
        return True

    def record(self, user_id: int, now: float) -> None:
        self.global_last_reply_at = now
        self.last_user_id = user_id
        self.user_last_reply_at[user_id] = now


_throttle = CommunityThrottle()


def _is_bot_or_command(update: Update) -> bool:
    user = update.effective_user
    message = update.effective_message
    text = message.text if message else ''
    return bool((user and user.is_bot) or (text and text.startswith('/')))


def _match_auto_reply(text: str) -> tuple[str, str | None, bool] | None:
    message = normalize_message(text)
    words = set(message.split())
    if message in MORNING_GREETINGS:
        return random.choice(MORNING_REPLIES), 'GOOD_MORNING', True
    if message in GENERAL_GREETINGS:
        return random.choice(GENERAL_REPLIES), random.choice(['GREETING', 'WELCOME']), True
    if message in AFTERNOON_GREETINGS:
        return random.choice(AFTERNOON_REPLIES), None, True
    if message in EVENING_GREETINGS:
        return random.choice(EVENING_REPLIES), None, True
    if message in GOOD_NIGHT_GREETINGS:
        return random.choice(GOOD_NIGHT_REPLIES), None, True
    if words & KEYWORDS and random.random() < 0.25:
        return random.choice(KEYWORD_REPLIES), None, False
    return None


async def handle_auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not settings.enable_auto_replies or _is_bot_or_command(update):
        return
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat or not message.text:
        return
    match = _match_auto_reply(message.text)
    if not match:
        return
    now = time.monotonic()
    if not _throttle.can_reply(user.id, now):
        return
    text, image_kind, _ = match
    await send_with_optional_image(context.bot, chat.id, text, image_kind)
    _throttle.record(user.id, now)


async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not settings.enable_welcome_messages:
        return
    message = update.effective_message
    chat = update.effective_chat
    if not message or not chat or not message.new_chat_members:
        return
    for member in message.new_chat_members:
        if member.is_bot:
            continue
        await send_with_optional_image(context.bot, chat.id, random.choice(WELCOME_REPLIES), 'WELCOME')


async def goodbye_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not settings.enable_goodbye_messages:
        return
    message = update.effective_message
    chat = update.effective_chat
    if not message or not chat or not message.left_chat_member or message.left_chat_member.is_bot:
        return
    await send_with_optional_image(context.bot, chat.id, random.choice(GOODBYE_REPLIES))
