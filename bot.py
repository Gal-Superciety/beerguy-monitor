"""BeerGuy Monitor Telegram bot entry point."""
from __future__ import annotations

import logging

from telegram.ext import Application, CommandHandler

from commands.chart import chart_command
from commands.contract import contract_command
from commands.holders import holders_command
from commands.info import help_command, info_command
from commands.price import price_command
from commands.raid import raid_command
from config import settings
from services.alerts import AlertService
from services.dexscreener import DexScreenerClient
from services.holders import HolderService
from services.price import PriceService
from services.solana import SolanaClient
from utils.logger import setup_logging

LOGGER = logging.getLogger(__name__)


def build_application() -> Application:
    """Create and configure the python-telegram-bot application."""
    settings.validate()
    application = Application.builder().token(settings.telegram_token).post_init(post_init).build()

    solana = SolanaClient(settings.solana_rpc, settings.token_mint)
    dex = DexScreenerClient(settings.token_mint, settings.dexscreener_api_url)
    application.bot_data["price_service"] = PriceService(dex, settings.dexscreener_url)
    application.bot_data["holder_service"] = HolderService(solana)
    application.bot_data["alert_service"] = AlertService(application.bot, solana, settings)

    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("chart", chart_command))
    application.add_handler(CommandHandler("contract", contract_command))
    application.add_handler(CommandHandler("holders", holders_command))
    application.add_handler(CommandHandler("raid", raid_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    return application


async def post_init(application: Application) -> None:
    """Start background alert polling after Telegram initialization."""
    alert_service: AlertService = application.bot_data["alert_service"]
    application.create_task(alert_service.run_forever())
    LOGGER.info("BeerGuy alert polling started")


def main() -> None:
    """Run BeerGuy Monitor until interrupted."""
    setup_logging()
    application = build_application()
    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
