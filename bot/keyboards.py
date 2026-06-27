from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import settings
def public_menu():
    rows=[[InlineKeyboardButton('📈 Price', callback_data='price'),InlineKeyboardButton('💧 Liquidity', callback_data='liquidity')],[InlineKeyboardButton('👥 Holders', callback_data='holders'),InlineKeyboardButton('🛒 Buy', url=settings.buy_url or 'https://jup.ag')],[InlineKeyboardButton('📊 Chart', url=settings.chart_url or 'https://dexscreener.com/solana')]]
    return InlineKeyboardMarkup(rows)
def admin_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton('🧪 Test alert', callback_data='testalert'),InlineKeyboardButton('✅ Status', callback_data='status')]])
