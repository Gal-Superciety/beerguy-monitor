from __future__ import annotations

import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field

from utils.link_checker import check_links

_NORMALIZE_RE = re.compile(r'\s+')
DM_SCAM_RE = re.compile(r'(?i)\b(dm|message|contact|inbox)\b.{0,30}\b(admin|support|moderator|helpdesk|agent)\b|\badmin\b.{0,30}\b(dm|message|contact)\b')
UNRELATED_AD_RE = re.compile(r'(?i)\b(presale|fairlaunch|100x|gem|ape|pump)\b.{0,80}\b(join|buy|launch|ca:|contract)\b')


@dataclass(frozen=True)
class SpamResult:
    is_spam: bool
    reason: str = ''
    severity: str = 'low'


@dataclass
class UserWindow:
    messages: deque[tuple[float, str]] = field(default_factory=deque)
    links: deque[float] = field(default_factory=deque)
    warnings: int = 0


class SpamDetector:
    def __init__(self, window_seconds: int = 20, max_messages: int = 8, repeat_threshold: int = 3, link_window_seconds: int = 60, max_links: int = 5):
        self.window_seconds = window_seconds
        self.max_messages = max_messages
        self.repeat_threshold = repeat_threshold
        self.link_window_seconds = link_window_seconds
        self.max_links = max_links
        self.users: dict[tuple[int, int], UserWindow] = defaultdict(UserWindow)

    @staticmethod
    def normalize(text: str) -> str:
        return _NORMALIZE_RE.sub(' ', (text or '').casefold()).strip()

    def check(self, chat_id: int, user_id: int, text: str, now: float | None = None) -> SpamResult:
        now = now or time.monotonic()
        normalized = self.normalize(text)
        link_result = check_links(text)
        if link_result.suspicious:
            return SpamResult(True, link_result.reason, 'high')
        if DM_SCAM_RE.search(text or ''):
            return SpamResult(True, 'fake support or DM scam', 'high')
        if UNRELATED_AD_RE.search(text or '') and '$bguy' not in normalized and 'beerguy' not in normalized:
            return SpamResult(True, 'unrelated crypto advertisement', 'medium')

        state = self.users[(chat_id, user_id)]
        while state.messages and now - state.messages[0][0] > self.window_seconds:
            state.messages.popleft()
        while state.links and now - state.links[0] > self.link_window_seconds:
            state.links.popleft()

        if normalized:
            state.messages.append((now, normalized))
        if link_result.urls:
            state.links.append(now)

        if normalized and sum(1 for _, msg in state.messages if msg == normalized) >= self.repeat_threshold:
            return SpamResult(True, 'repeated identical messages', 'medium')
        if len(state.messages) > self.max_messages:
            return SpamResult(True, 'message flood', 'medium')
        if len(state.links) > self.max_links:
            return SpamResult(True, 'excessive repeated links', 'medium')
        return SpamResult(False)

    def record_warning(self, chat_id: int, user_id: int) -> int:
        state = self.users[(chat_id, user_id)]
        state.warnings += 1
        return state.warnings
