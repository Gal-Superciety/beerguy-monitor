import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import settings
from bot import commands
from bot.callbacks import handle_callback
from bot.alerts import send_with_optional_image
from services.replies import match_reply
from services.price import price_text
from services.community import handle_auto_reply, welcome_new_members, goodbye_member
from services.moderation import moderate_message
logging.basicConfig(level=logging.INFO)
async def fixed_replies(update, context):
    reply=match_reply(update.effective_message.text or '')
    if not reply: return
    text = await price_text() if reply.dynamic == 'price' else reply.text
    await send_with_optional_image(context.bot, update.effective_chat.id, text, reply.image_kind)
def build_application():
    settings.validate(); app=Application.builder().token(settings.telegram_bot_token).build()
    for name in ['start','menu','status','price','liquidity','holders','buy','chart','contract','raid','links','info','help','testalert','admin']:
        app.add_handler(CommandHandler(name, getattr(commands, name)))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye_member))
    message_content = filters.TEXT | filters.CaptionRegex(r'.+')
    app.add_handler(MessageHandler(message_content & ~filters.COMMAND, moderate_message), group=0)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_auto_reply), group=1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fixed_replies), group=2)
    return app
def main(): build_application().run_polling(close_loop=False)
if __name__ == '__main__': main()
