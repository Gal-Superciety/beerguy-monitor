from types import SimpleNamespace

from services.leaderboard import LeaderboardService, LeaderboardStorage


class MemoryStore:
    def __init__(self):
        self.value = LeaderboardStorage._empty()

    def read(self):
        return self.value

    def write(self, value):
        self.value = value


def update(text='Great BeerGuy raid update', *, user_id=1, username='user1', reply=False, bot=False, photo=False):
    user = SimpleNamespace(id=user_id, username=username, first_name='User', is_bot=bot)
    replied = SimpleNamespace(from_user=SimpleNamespace(id=999)) if reply else None
    message = SimpleNamespace(
        text=text,
        caption=None,
        photo=[SimpleNamespace(file_unique_id='p1')] if photo else None,
        animation=None,
        video=None,
        sticker=None,
        document=None,
        reply_to_message=replied,
        chat_id=-100,
        new_chat_members=None,
    )
    return SimpleNamespace(effective_user=user, effective_message=message)


def service():
    return LeaderboardService(LeaderboardStorage(MemoryStore()))


def test_scores_useful_reply_message():
    decision = service().score_message(update('BeerGuy raid and holder chart looks bullish today', reply=True))
    assert decision.points == 6


def test_ignores_short_low_value_messages():
    assert service().score_message(update('lol')).points == 0


def test_repeated_message_does_not_count_twice():
    lb = service()
    assert lb.record_activity(update('BeerGuy raid and holder chart looks bullish today')) == 4
    assert lb.record_activity(update('BeerGuy raid and holder chart looks bullish today')) == 0


def test_formats_top_raider():
    lb = service()
    lb.record_activity(update('BeerGuy raid and holder chart looks bullish today'))
    text = lb.format_leaderboard()
    assert 'Weekly Beer Raiders Leaderboard' in text
    assert '@user1' in text


def test_weekly_points_are_unlimited_by_daily_cap():
    from services.leaderboard import settings

    lb = service()
    original_cooldown = settings.leaderboard_message_cooldown_seconds
    object.__setattr__(settings, 'leaderboard_message_cooldown_seconds', 0)
    try:
        total = 0
        for idx in range(10):
            total += lb.record_activity(update(f'BeerGuy raid holder chart looks bullish update number {idx}'))
    finally:
        object.__setattr__(settings, 'leaderboard_message_cooldown_seconds', original_cooldown)

    data = lb.storage.read()
    assert total == 40
    assert data['users']['1']['weekly_points'] == 40
    assert 'daily_points' not in data['users']['1']
