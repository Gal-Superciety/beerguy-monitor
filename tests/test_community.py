from services.community import _match_auto_reply, normalize_message


def test_general_greeting_gets_image():
    reply = _match_auto_reply('bună')
    assert reply is not None
    assert reply[1] in {'GREETING', 'WELCOME'}


def test_good_morning_gets_good_morning_image():
    reply = _match_auto_reply('bună dimineața')
    assert reply is not None
    assert reply[1] == 'GOOD_MORNING'


def test_keyword_normalization():
    assert normalize_message('Cheers, BeerGuy!') == 'cheers beerguy'
