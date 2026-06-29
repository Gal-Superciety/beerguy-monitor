from pathlib import Path

import pytest

from bot.alerts import send_optional_photo


@pytest.mark.asyncio
async def test_send_optional_photo_falls_back_for_empty_file(tmp_path):
    empty_photo = tmp_path / 'welcome.png'
    empty_photo.touch()
    calls = []

    async def send_photo(photo):
        calls.append(('photo', photo))

    async def send_text(message):
        calls.append(('text', message))
        return message

    result = await send_optional_photo(empty_photo, 'welcome text', send_photo, send_text)

    assert result == 'welcome text'
    assert calls == [('text', 'welcome text')]


@pytest.mark.asyncio
async def test_send_optional_photo_sends_existing_non_empty_file(tmp_path):
    photo_path = tmp_path / 'welcome.png'
    photo_path.write_bytes(b'not empty')
    calls = []

    async def send_photo(photo):
        calls.append(('photo', Path(photo.name).name, photo.read()))
        return 'sent photo'

    async def send_text(message):
        calls.append(('text', message))

    result = await send_optional_photo(photo_path, 'welcome text', send_photo, send_text)

    assert result == 'sent photo'
    assert calls == [('photo', 'welcome.png', b'not empty')]
