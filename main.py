# main.py
import logging
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Market Bot starting...")

    # Start background scheduler
    from core.scheduler import start_scheduler
    scheduler = start_scheduler()

    # Build Telegram bot
    from bot.handlers import (
        start_command, add_command, remove_command,
        watchlist_command, price_command, alert_command,
        general_message, graph_command, compare_command, button_callback, stats_command, news_command
    )

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    # Register all command handlers
    app.add_handler(CommandHandler("start",     start_command))
    app.add_handler(CommandHandler("add",       add_command))
    app.add_handler(CommandHandler("remove",    remove_command))
    app.add_handler(CommandHandler("watchlist", watchlist_command))
    app.add_handler(CommandHandler("price",     price_command))
    app.add_handler(CommandHandler("alert",     alert_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, general_message))
    app.add_handler(CommandHandler("graph", graph_command))
    app.add_handler(CommandHandler("compare", compare_command))

    # Register command handlers
    app.add_handler(CommandHandler("start",     start_command))
    app.add_handler(CommandHandler("add",       add_command))
    app.add_handler(CommandHandler("remove",    remove_command))
    app.add_handler(CommandHandler("watchlist", watchlist_command))
    app.add_handler(CommandHandler("price",     price_command))
    app.add_handler(CommandHandler("alert",     alert_command))
    app.add_handler(CommandHandler("compare",   compare_command))
    app.add_handler(CommandHandler("stats",     stats_command))
    app.add_handler(CommandHandler("graph",     graph_command))
    app.add_handler(CommandHandler("news", news_command))

    app.add_handler(CallbackQueryHandler(button_callback))  # ← add this

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, general_message))




    logger.info("Bot is running. Press Ctrl+C to stop.")

    # run_polling() blocks here and keeps everything alive
    # It replaces our old while True: time.sleep(60) loop
    app.run_polling()

    # Only reaches here after Ctrl+C
    scheduler.shutdown()
    logger.info("Goodbye!")


if __name__ == "__main__":
    main()