from telegram import Update
from telegram.ext import ContextTypes
from config import settings
from bot.keyboards import public_menu, admin_menu
from bot.alerts import send_with_optional_image, broadcast_alert
from services.price import price_text
from services.liquidity import liquidity_text
from services.holders import holders_text
from services.status import status_text
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.effective_message.reply_html('🍺 <b>BeerGuy Monitor</b>\nMonitorizare BGUY pe Solana.', reply_markup=public_menu())
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.effective_message.reply_text('BeerGuy menu:', reply_markup=public_menu())
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user and update.effective_user.id == settings.admin_telegram_id: await update.effective_message.reply_text('Admin menu:', reply_markup=admin_menu())
async def status(update, context): await update.effective_message.reply_html(await status_text())
async def price(update, context): await update.effective_message.reply_html(await price_text(), disable_web_page_preview=True)
async def liquidity(update, context): await update.effective_message.reply_html(await liquidity_text())
async def holders(update, context): await update.effective_message.reply_html(await holders_text())
async def buy(update, context): await send_with_optional_image(context.bot, update.effective_chat.id, f'🛒 Buy BGUY: {settings.buy_url or "BUY_URL neconfigurat"}', 'BUY')
async def chart(update, context): await update.effective_message.reply_text(f'📊 Chart: {settings.chart_url or "CHART_URL neconfigurat"}')
async def testalert(update, context): await broadcast_alert(context.bot, '🧪 <b>Test alert BeerGuy</b>', 'BUY')
