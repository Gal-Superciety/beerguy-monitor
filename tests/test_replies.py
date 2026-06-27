from services.replies import match_reply, normalize_message
def test_greetings_are_handled_by_community_service():
    assert match_reply('Hi') is None
    assert match_reply('gm') is None
def test_accents_buy(): assert normalize_message('preț') == 'pret'
