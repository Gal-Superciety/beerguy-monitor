from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import settings

DEFAULT_WEBSITE_URL = 'https://beerguy.io'
DEFAULT_TWITTER_URL = 'https://x.com/BeerGuySol'
DEFAULT_TELEGRAM_URL = 'https://t.me/BeerGuySol'
DEFAULT_CHART_URL = 'https://dexscreener.com/solana'
DEFAULT_BUY_URL = 'https://jup.ag'

def _contract_url() -> str | None:
    return f'https://solscan.io/token/{settings.token_mint}' if settings.token_mint else None

def premium_start_menu():
    rows = [
        [InlineKeyboardButton('🌐 Website', url=settings.website_url or DEFAULT_WEBSITE_URL), InlineKeyboardButton('🐦 X (Twitter)', url=settings.twitter_url or DEFAULT_TWITTER_URL)],
        [InlineKeyboardButton('💬 Telegram', url=settings.telegram_url or DEFAULT_TELEGRAM_URL)],
        [InlineKeyboardButton('📄 Contract', url=_contract_url()) if _contract_url() else InlineKeyboardButton('📄 Contract', callback_data='contract'), InlineKeyboardButton('📈 Chart', url=settings.chart_url or DEFAULT_CHART_URL)],
        [InlineKeyboardButton('Price', callback_data='price'), InlineKeyboardButton('Chart', callback_data='chart')],
        [InlineKeyboardButton('Holders', callback_data='holders'), InlineKeyboardButton('Contract', callback_data='contract')],
        [InlineKeyboardButton('Liquidity', callback_data='liquidity'), InlineKeyboardButton('Buy', url=settings.buy_url or DEFAULT_BUY_URL)],
        [InlineKeyboardButton('Raid', callback_data='raid'), InlineKeyboardButton('Links', callback_data='links')],
        [InlineKeyboardButton('Info', callback_data='info'), InlineKeyboardButton('Help', callback_data='help')],
    ]
    return InlineKeyboardMarkup(rows)

def public_menu():
    return premium_start_menu()

def admin_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton('🧪 Test alert', callback_data='testalert'),InlineKeyboardButton('✅ Status', callback_data='status')]])
