from pathlib import Path
from config import ASSETS_DIR
IMAGE_MAP = {
 'BUY':'buy.png','SELL':'sell.png','BIG_BUY':'big_buy.png','BIG_SELL':'big_sell.png','LIQUIDITY':'liquidity.png',
 'LIQUIDITY_ADD':'liquidity.png','LIQUIDITY_REMOVE':'liquidity.png','NEW_HOLDER':'new_holder.png','WHALE':'whale.png','BURN':'burn.png',
 'GOOD_MORNING':'good_morning.png','GREETING':'greeting.png','WELCOME':'welcome.png','GIVEAWAY':'giveaway.png','CONTEST':'contest.png',
 'ANNOUNCEMENT':'announcement.png','LOADING':'loading.png','RAID':'raid.png','PRICE_MILESTONE':'price_milestone.png','HOLDER_MILESTONE':'holder_milestone.png'}
def image_path(kind: str) -> Path | None:
    path = ASSETS_DIR / IMAGE_MAP.get(kind.upper(), kind)
    return path if path.exists() else None
