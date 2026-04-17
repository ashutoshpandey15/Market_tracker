# main.py
import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def _validate_env():
    """Fail fast with a clear message if required env vars are missing."""
    required = {
        "TELEGRAM_BOT_TOKEN": "Get this from @BotFather on Telegram",
        "SUPABASE_URL":        "Your Supabase project URL",
        "SUPABASE_KEY":        "Your Supabase anon/service key",
    }
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        for key in missing:
            logger.error(f"Missing required env var: {key}  ({required[key]})")
        sys.exit(1)


def main():
    _validate_env()

    logger.info("Market Bot starting...")

    # Import handlers (also imports database — safe now that env vars are confirmed present)
    from telegram.ext import (
        ApplicationBuilder, CommandHandler,
        MessageHandler, filters, CallbackQueryHandler
    )
    from bot.handlers import (
        start_command, add_command, remove_command,
        watchlist_command, price_command, alert_command,
        general_message, graph_command, compare_command,
        button_callback, stats_command, news_command
    )

    # Build Telegram bot
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    # Register handlers (once each)
    app.add_handler(CommandHandler("start",     start_command))
    app.add_handler(CommandHandler("add",       add_command))
    app.add_handler(CommandHandler("remove",    remove_command))
    app.add_handler(CommandHandler("watchlist", watchlist_command))
    app.add_handler(CommandHandler("price",     price_command))
    app.add_handler(CommandHandler("alert",     alert_command))
    app.add_handler(CommandHandler("graph",     graph_command))
    app.add_handler(CommandHandler("compare",   compare_command))
    app.add_handler(CommandHandler("stats",     stats_command))
    app.add_handler(CommandHandler("news",      news_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, general_message))

    # Start background scheduler (non-blocking)
    from core.scheduler import start_scheduler
    scheduler = start_scheduler()

    logger.info("Bot is running. Press Ctrl+C to stop.")

    # run_polling() blocks here and keeps everything alive
    app.run_polling()

    # Only reaches here after Ctrl+C
    scheduler.shutdown()
    logger.info("Goodbye!")


if __name__ == "__main__":
    main()
