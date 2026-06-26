"""Community admin-style Telegram interactions for BeerGuy."""
from __future__ import annotations

import random
import re
import time
import unicodedata

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from utils.branding import reply_branded_html, with_footer
from utils.keyboards import official_links_keyboard

WELCOME_MESSAGES = (
    "🍺 <b>Welcome, Raider!</b>\n\n"
    "A new Beer Raider has entered the tavern.\n\n"
    "Grab a mug, join the crew, and get ready to Brew. Farm. Raid.\n\n"
    "⚔️ <b>Welcome to BeerGuy!</b>",
    "🍺 <b>A new Viking has joined the longship!</b>\n\n"
    "Welcome to the BeerGuy community, Raider.\n\n"
    "Check our official links below and stay close for updates.",
    "⚔️ <b>Welcome aboard, Beer Raider!</b>\n\n"
    "The tavern is warm, the crew is ready, and the raids never sleep.\n\n"
    "Use the official links below to stay connected.",
)

GREETING_REPLIES = (
    "🍺 <b>Good morning, Beer Raiders!</b>\n\n"
    "The tavern is open and the longship is ready.",
    "<b>GM Raider</b> 🍺\n\n"
    "New day, new raids, same BeerGuy energy.\n\n"
    "Stay strong and keep building.",
    "<b>Salut, Raider!</b> 🍺\n\n"
    "Bine ai venit în tavernă.\n\n"
    "Verifică linkurile oficiale și rămâi aproape de comunitate.",
    "🍺 <b>Hey Raider!</b>\n\n"
    "Good to see you in the BeerGuy tavern. Keep it friendly, loud, and legendary.",
)

GREETING_PHRASES = {
    "good morning",
    "gm",
    "gm raiders",
    "morning",
    "hello",
    "hi",
    "hey",
    "salut",
    "buna",
    "buna dimineata",
    "neata",
    "servus",
    "ciao",
}

LINK_KEYWORDS = {"contract", "ca", "website", "site", "twitter", "x", "telegram", "chart", "links"}
LINKS_TEXT = with_footer(
    "🍺 <b>Official BeerGuy Links</b>\n\n"
    "Use only official BeerGuy community links below, Raider."
)

_WORD_RE = re.compile(r"[\wăâîșşțţ]+", re.IGNORECASE)


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(_normalize(text))


def _is_greeting(text: str) -> bool:
    clean = " ".join(_words(text))
    if not clean:
        return False
    if clean in GREETING_PHRASES:
        return True
    return any(clean.startswith(f"{phrase} ") for phrase in GREETING_PHRASES)


def _is_link_request(text: str) -> bool:
    return bool(set(_words(text)) & LINK_KEYWORDS)


async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome each newly joined non-bot member with official BeerGuy links."""
    message = update.effective_message
    if message is None or not message.new_chat_members:
        return
    for member in message.new_chat_members:
        if member.is_bot:
            continue
        await reply_branded_html(
            message,
            with_footer(random.choice(WELCOME_MESSAGES)),
            reply_markup=official_links_keyboard(include_contract_callback=False),
        )


async def community_text_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to greetings and official-link requests without spamming the group."""
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if message is None or user is None or chat is None or not message.text:
        return

    if _is_link_request(message.text):
        await reply_branded_html(
            message,
            LINKS_TEXT,
            reply_markup=official_links_keyboard(include_contract_callback=False),
        )
        return

    if not _is_greeting(message.text):
        return

    now = time.monotonic()
    user_key = (chat.id, user.id)
    last_by_user = context.application.bot_data.setdefault("community_greeting_user_last", {})
    last_by_chat = context.application.bot_data.setdefault("community_greeting_chat_last", {})
    if now - last_by_user.get(user_key, 0.0) < settings.greeting_user_cooldown_seconds:
        return
    if now - last_by_chat.get(chat.id, 0.0) < settings.greeting_group_cooldown_seconds:
        return

    last_by_user[user_key] = now
    last_by_chat[chat.id] = now
    await reply_branded_html(
        message,
        with_footer(random.choice(GREETING_REPLIES)),
        reply_markup=official_links_keyboard(include_contract_callback=False),
    )
