import unicodedata, re
from dataclasses import dataclass
from config import settings
_WORD_RE=re.compile(r'[\wăâîșşțţ]+', re.I)
@dataclass(frozen=True)
class FixedReply:
    text: str; image_kind: str|None=None; dynamic: str|None=None
def normalize_message(text: str) -> str:
    n=unicodedata.normalize('NFKD', text.casefold())
    n=''.join(c for c in n if not unicodedata.combining(c))
    return ' '.join(_WORD_RE.findall(n))
def match_reply(text: str) -> FixedReply|None:
    m=normalize_message(text)
    if m in {'buy','how to buy','unde cumpar'}: return FixedReply(f'🛒 Cumpără BGUY aici: {settings.buy_url or "BUY_URL neconfigurat"}', 'BUY')
    if m in {'chart','grafic'}: return FixedReply(f'📈 Chart BGUY: {settings.chart_url or "CHART_URL neconfigurat"}')
    if m in {'price','pret'}: return FixedReply('', dynamic='price')
    return None
