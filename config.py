from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / 'assets' / 'images'
DATA_DIR = BASE_DIR / 'data'
def _bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {'1','true','yes','on'}
def _int(name, default=0):
    try: return int(os.getenv(name, default) or default)
    except ValueError: return default
def _float(name, default=0.0):
    try: return float(os.getenv(name, default) or default)
    except ValueError: return default
@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str = os.getenv('TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_TOKEN',''))
    admin_telegram_id: int = _int('ADMIN_TELEGRAM_ID', 0)
    telegram_private_chat_id: str = os.getenv('TELEGRAM_PRIVATE_CHAT_ID', os.getenv('TELEGRAM_CHAT_ID',''))
    enable_private_alerts: bool = _bool('ENABLE_PRIVATE_ALERTS', True)
    telegram_group_chat_id: str = os.getenv('TELEGRAM_GROUP_CHAT_ID','')
    enable_group_alerts: bool = _bool('ENABLE_GROUP_ALERTS', False)
    solana_rpc_url: str = os.getenv('SOLANA_RPC_URL', os.getenv('SOLANA_RPC','https://api.mainnet-beta.solana.com'))
    solana_ws_url: str = os.getenv('SOLANA_WS_URL','')
    helius_api_key: str = os.getenv('HELIUS_API_KEY','')
    birdeye_api_key: str = os.getenv('BIRDEYE_API_KEY','')
    token_symbol: str = os.getenv('TOKEN_SYMBOL','BGUY')
    token_mint: str = os.getenv('TOKEN_MINT','')
    token_decimals: int = _int('TOKEN_DECIMALS', 6)
    quote_symbol: str = os.getenv('QUOTE_SYMBOL','SOL')
    quote_mint: str = os.getenv('QUOTE_MINT','So11111111111111111111111111111111111111112')
    price_url: str = os.getenv('PRICE_URL','')
    chart_url: str = os.getenv('CHART_URL','')
    buy_url: str = os.getenv('BUY_URL','')
    twitter_url: str = os.getenv('TWITTER_URL','')
    website_url: str = os.getenv('WEBSITE_URL','')
    telegram_url: str = os.getenv('TELEGRAM_URL','')
    min_alert_usd: float = _float('MIN_ALERT_USD', 25)
    big_alert_usd: float = _float('BIG_ALERT_USD', 500)
    whale_alert_usd: float = _float('WHALE_ALERT_USD', 2500)
    poll_interval: int = _int('POLL_INTERVAL', 20)
    enable_auto_replies: bool = _bool('ENABLE_AUTO_REPLIES', True)
    enable_welcome_messages: bool = _bool('ENABLE_WELCOME_MESSAGES', True)
    enable_goodbye_messages: bool = _bool('ENABLE_GOODBYE_MESSAGES', False)
    auto_reply_cooldown: int = _int('AUTO_REPLY_COOLDOWN', 60)
    leaderboard_enabled: bool = _bool('LEADERBOARD_ENABLED', True)
    leaderboard_post_day: str = os.getenv('LEADERBOARD_POST_DAY', 'saturday')
    leaderboard_post_hour: int = _int('LEADERBOARD_POST_HOUR', 18)
    leaderboard_timezone: str = os.getenv('LEADERBOARD_TIMEZONE', 'Europe/Berlin')
    leaderboard_message_cooldown_seconds: int = _int('LEADERBOARD_MESSAGE_COOLDOWN_SECONDS', 60)
    def validate(self):
        if not self.telegram_bot_token:
            raise RuntimeError('Missing TELEGRAM_BOT_TOKEN')
settings = Settings()
