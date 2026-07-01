from types import SimpleNamespace

from services.leaderboard import LeaderboardService, LeaderboardStorage


class MemoryStore:
    def __init__(self, value=None):
        self.value = value if value is not None else LeaderboardStorage._empty()

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


def service(store=None, event_store=None):
    return LeaderboardService(LeaderboardStorage(store or MemoryStore(), event_store or MemoryStore(LeaderboardStorage._empty_events())))


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


def test_weekly_points_are_capped_weekly_not_daily():
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


def test_preserves_existing_points_when_recording_after_migration():
    store = MemoryStore({
        'users': {
            '1': {
                'id': 1,
                'username': 'olduser',
                'first_name': 'Old',
                'weekly_points': 1498,
                'daily_points': 30,
                'week_key': service().week_key(),
                'last_scored_at': '1970-01-01T00:00:00+00:00',
                'scored_messages': [],
            }
        }
    })
    lb = service(store=store)

    awarded = lb.record_activity(update('BeerGuy raid holder chart looks bullish new cap message'))

    data = lb.storage.read()
    assert awarded == 2
    assert data['users']['1']['weekly_points'] == 1500
    assert 'daily_points' not in data['users']['1']


def test_user_at_weekly_cap_gets_no_more_points():
    store = MemoryStore({
        'users': {
            '1': {
                'id': 1,
                'username': 'capped',
                'first_name': 'Cap',
                'weekly_points': 1500,
                'week_key': service().week_key(),
                'last_scored_at': '1970-01-01T00:00:00+00:00',
                'scored_messages': [],
            }
        }
    })
    lb = service(store=store)

    assert lb.record_activity(update('BeerGuy raid holder chart looks bullish over cap')) == 0
    assert lb.storage.read()['users']['1']['weekly_points'] == 1500


def test_rebuild_from_persisted_activity_events():
    week = service().week_key()
    store = MemoryStore()
    events = MemoryStore({
        'events': [
            {'week_key': week, 'user_id': 1, 'username': 'user1', 'first_name': 'User', 'points': 4, 'signature': 'a', 'scored_at': '2026-07-01T00:00:00+00:00'},
            {'week_key': week, 'user_id': 1, 'username': 'user1', 'first_name': 'User', 'points': 4, 'signature': 'b', 'scored_at': '2026-07-01T00:01:00+00:00'},
        ],
        'schema_version': 1,
    })
    lb = service(store=store, event_store=events)

    users, points = lb.rebuild_from_events()

    assert (users, points) == (1, 8)
    assert lb.storage.read()['users']['1']['weekly_points'] == 8


def test_format_preserves_existing_scores_until_explicit_weekly_reset():
    store = MemoryStore({
        'users': {
            '1': {
                'id': 1,
                'username': 'preserved',
                'first_name': 'Preserved',
                'weekly_points': 123,
                'week_key': 'legacy-week',
                'last_scored_at': '1970-01-01T00:00:00+00:00',
                'scored_messages': [],
            }
        }
    })
    lb = service(store=store)

    text = lb.format_leaderboard()

    assert '@preserved' in text
    assert '123 points' in text
