from telegram import Update
from telegram.ext import ContextTypes
from bot.commands import buy, chart, contract, help, holders, info, links, liquidity, price, raid, status, testalert

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    name=q.data
    fake=Update(update.update_id, message=q.message)
    if name=='price': await price(fake, context)
    elif name=='liquidity': await liquidity(fake, context)
    elif name=='holders': await holders(fake, context)
    elif name=='status': await status(fake, context)
    elif name=='chart': await chart(fake, context)
    elif name=='contract': await contract(fake, context)
    elif name=='buy': await buy(fake, context)
    elif name=='raid': await raid(fake, context)
    elif name=='links': await links(fake, context)
    elif name=='info': await info(fake, context)
    elif name=='help': await help(fake, context)
    elif name=='testalert': await testalert(fake, context)
