from services.replies import match_reply, normalize_message
def test_hi_is_not_gm():
    reply = match_reply('Hi')
    assert reply and reply.image_kind == 'GREETING'
    assert 'Good morning' not in reply.text
def test_gm_is_good_morning(): assert match_reply('gm').image_kind == 'GOOD_MORNING'
def test_accents_buy(): assert normalize_message('preț') == 'pret'
