from telegram import Update
from telegram.ext import ContextTypes
from config import settings
from bot.keyboards import admin_menu, premium_start_menu, public_menu
from bot.alerts import send_optional_photo, send_with_optional_image, broadcast_alert
from services.price import price_text
from services.liquidity import liquidity_text
from services.holders import holders_text
from services.status import status_text
from storage.files import image_path
from services.leaderboard import leaderboard_command as leaderboard, leaderboard_reset, leaderboard_rebuild, leaderboard_export, leaderboard_pause, leaderboard_resume

WELCOME_MESSAGE = """🍺 *Welcome to BeerGuy Monitor*

*The official market intelligence hub for BeerGuy (BGUY).*\n\nTrack the BeerGuy ecosystem with fast access to live market data, liquidity insights, holder metrics, contract details, and community resources — all from one premium command center.\n\n✨ *Built for holders, raiders, and serious community members.*\n\n🔎 *Monitor the market*\n📊 *Follow the chart*\n💧 *Check liquidity*\n👥 *Watch holder growth*\n⚡ *Move quickly with trusted links*\n\n_Brew. Farm. Raid._"""

def _contract_url() -> str | None:
    return f'https://solscan.io/token/{settings.token_mint}' if settings.token_mint else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = image_path('WELCOME')

    async def send_photo(photo):
        return await update.effective_message.reply_photo(photo=photo)

    async def send_text(message: str):
        return await update.effective_message.reply_markdown(message, reply_markup=premium_start_menu())

    await send_optional_photo(
        welcome,
        WELCOME_MESSAGE,
        send_photo,
        send_text,
        fallback_log='Welcome image not found.\nSending text-only welcome.',
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.effective_message.reply_text('BeerGuy command center:', reply_markup=public_menu())
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user and update.effective_user.id == settings.admin_telegram_id: await update.effective_message.reply_text('Admin menu:', reply_markup=admin_menu())
async def status(update, context): await update.effective_message.reply_html(await status_text())
async def price(update, context): await update.effective_message.reply_html(await price_text(), disable_web_page_preview=True)
async def liquidity(update, context): await update.effective_message.reply_html(await liquidity_text())
async def holders(update, context): await update.effective_message.reply_html(await holders_text())
async def buy(update, context): await send_with_optional_image(context.bot, update.effective_chat.id, f'🛒 Buy BGUY: {settings.buy_url or "BUY_URL not configured"}', 'BUY')
async def chart(update, context): await update.effective_message.reply_text(f'📈 Chart: {settings.chart_url or "CHART_URL not configured"}')
async def contract(update, context): await update.effective_message.reply_html(f'📄 <b>Contract</b>\n<code>{settings.token_mint or "TOKEN_MINT not configured"}</code>')
async def raid(update, context): await send_with_optional_image(context.bot, update.effective_chat.id, '⚔️ <b>BeerGuy Raid Center</b>\n\nRally the community, share the official links, and keep the BeerGuy energy moving.\n\nBrew. Farm. Raid.', 'RAID')
async def links(update, context):
    lines = ['🔗 <b>Official BeerGuy Links</b>']
    if settings.website_url: lines.append(f'🌐 Website: {settings.website_url}')
    if settings.twitter_url: lines.append(f'🐦 X (Twitter): {settings.twitter_url}')
    if settings.telegram_url: lines.append(f'💬 Telegram: {settings.telegram_url}')
    if settings.chart_url: lines.append(f'📈 Chart: {settings.chart_url}')
    if settings.buy_url: lines.append(f'🛒 Buy: {settings.buy_url}')
    if _contract_url(): lines.append(f'📄 Contract: {_contract_url()}')
    await update.effective_message.reply_html('\n'.join(lines), disable_web_page_preview=True)
async def info(update, context): await update.effective_message.reply_markdown(WELCOME_MESSAGE, reply_markup=premium_start_menu())
async def help(update, context): await update.effective_message.reply_text('BeerGuy Monitor commands: /price /chart /holders /contract /liquidity /buy /raid /links /info /help')
async def testalert(update, context): await broadcast_alert(context.bot, '🧪 <b>Test alert BeerGuy</b>', 'BUY')
