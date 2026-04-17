# core/scheduler.py
import logging
import os
from datetime import datetime
import pytz
import requests as req
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from api.market_api import get_price, get_price_history_api
from data.database import (
    get_watchlist, upsert_price,
    get_price_history, reset_alert_sent_flags, get_all_watchlist_symbols
)
from core.alerts import check_and_send_alerts

logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")
GOLD_TICKERS = {"GC=F", "GOLD", "XAU"}


# ─── Market Hours Check ───────────────────────────────────────
def _is_market_open() -> bool:
    now = datetime.now(IST)
    if now.weekday() >= 5:
        return False
    minutes = now.hour * 60 + now.minute
    return (9 * 60 + 15) <= minutes <= (15 * 60 + 30)


def _get_current_window(now_ist: datetime) -> str:
    minutes = now_ist.hour * 60 + now_ist.minute
    if minutes <= 10 * 60:
        return "OPENING"
    elif minutes <= 14 * 60 + 30:
        return "MID-DAY"
    else:
        return "CLOSING"


# ─── Core Fetch Functions ─────────────────────────────────────
def fetch_stock_prices():
    if not _is_market_open():
        logger.info("Market closed — skipping stock fetch")
        return

    watchlist = get_all_watchlist_symbols()
    # watchlist = get_watchlist()
    stock_tickers = [t for t in watchlist if t.upper() not in GOLD_TICKERS]

    if not stock_tickers:
        logger.info("No stocks in watchlist — skipping")
        return

    now_ist = datetime.now(IST)
    window = _get_current_window(now_ist)
    logger.info(f"[{window}] Fetching {len(stock_tickers)} stocks...")

    today = now_ist.strftime("%Y-%m-%d")
    for ticker in stock_tickers:
        result = get_price(ticker)
        if result:
            upsert_price(ticker, today, result["price"])
            logger.info(f"  {ticker}: ₹{result['price']}")
        else:
            logger.warning(f"  {ticker}: fetch failed")

    check_and_send_alerts()


def fetch_gold_price():
    """Fetch and save all gold karat prices at scheduled times."""
    # watchlist    = get_watchlist()
    watchlist = get_all_watchlist_symbols()
    gold_tickers = [t for t in watchlist if t.upper() in GOLD_TICKERS]

    if not gold_tickers:
        logger.info("No gold tickers in watchlist — skipping")
        return

    today = datetime.now(IST).strftime("%Y-%m-%d")

    # Always fetch all 3 karats in one scheduled run
    for karat_ticker in ["GOLD_24K", "GOLD_22K", "GOLD_18K"]:
        if karat_ticker in [t.upper() for t in gold_tickers]:
            result = get_price(karat_ticker)
            if result:
                upsert_price(karat_ticker, today, result["price"])
                logger.info(f"{karat_ticker}: ₹{result['price']}/10g saved")

    check_and_send_alerts()


def seed_price_history():
    # watchlist = get_watchlist()
    watchlist = get_all_watchlist_symbols()
    if not watchlist:
        return

    logger.info("Seeding 7-day price history...")
    for ticker in watchlist:
        history = get_price_history_api(ticker, days=7)
        for entry in history:
            upsert_price(ticker, entry["date"], entry["closing_price"])
        logger.info(f"  Seeded {len(history)} days for {ticker}")


# ─── Alert & Summary Functions ────────────────────────────────
# def send_eod_summary():
#     """
#     Send end of day performance summary at 3:45 PM IST.
#     Shows % change for every stock in watchlist vs previous day.
#     """
#     import os
#     import requests as req
#     from data.database import get_price_history

#     token = os.getenv("TELEGRAM_BOT_TOKEN")
#     today = datetime.now(IST).strftime("%Y-%m-%d")

#     # Get all users
#     try:
#         from data.database import supabase
#         users_result = supabase.table("bot_users").select("chat_id").execute()
#         chat_ids = [u["chat_id"] for u in users_result.data]
#     except Exception as e:
#         logger.error(f"EOD summary: failed to fetch users: {e}")
#         return

#     if not chat_ids:
#         return

#     watchlist = get_watchlist()
#     if not watchlist:
#         return

#     lines = [f"📊 *Market Summary — {today}*\n"]

#     for ticker in watchlist:
#         history = get_price_history(ticker, days=3)

#         if not history:
#             lines.append(f"➡️ `{ticker}` — no data")
#             continue

#         # Sort newest first
#         history = sorted(history, key=lambda x: x["date"], reverse=True)

#         # Find today's entry
#         today_entries = [e for e in history if e["date"] == today]
#         prev_entries  = [e for e in history if e["date"] != today]

#         if not today_entries:
#             lines.append(f"➡️ `{ticker}` — no data today")
#             continue

#         current = float(today_entries[0]["closing_price"])

#         if prev_entries:
#             prev       = float(prev_entries[0]["closing_price"])
#             change_pct = ((current - prev) / prev) * 100
#             change_abs = current - prev
#             arrow      = "📈" if change_pct >= 0 else "📉"
#             sign       = "+" if change_pct >= 0 else ""

#             lines.append(
#                 f"{arrow} `{ticker}`\n"
#                 f"    ₹{prev:,.2f} → ₹{current:,.2f}\n"
#                 f"    {sign}{change_abs:,.2f} ({sign}{change_pct:.2f}%)"
#             )
#         else:
#             lines.append(f"➡️ `{ticker}` — ₹{current:,.2f}")

#     message = "\n\n".join(lines)

#     # Send to all users
#     for chat_id in chat_ids:
#         try:
#             req.post(
#                 f"https://api.telegram.org/bot{token}/sendMessage",
#                 json={
#                     "chat_id":    chat_id,
#                     "text":       message,
#                     "parse_mode": "Markdown"
#                 },
#                 timeout=10
#             )
#         except Exception as e:
#             logger.error(f"EOD summary failed for {chat_id}: {e}")

#     logger.info(f"EOD summary sent to {len(chat_ids)} users ✅")


def reset_daily_alerts():
    """Reset all alert_sent flags at 9:00 AM every trading day."""
    reset_alert_sent_flags()

def send_eod_summary():
    """Send personalised EOD summary to each user based on their watchlist."""
    import os
    import requests as req
    from data.database import get_price_history, get_watchlist, supabase

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    today = datetime.now(IST).strftime("%Y-%m-%d")

    try:
        users_result = supabase.table("bot_users").select("chat_id").execute()
        chat_ids = [u["chat_id"] for u in users_result.data]
    except Exception as e:
        logger.error(f"EOD: failed to fetch users: {e}")
        return

    for chat_id in chat_ids:
        # Each user gets their own watchlist
        watchlist = get_watchlist(chat_id)
        if not watchlist:
            continue

        lines = [f"📊 *Market Summary — {today}*\n"]

        for ticker in watchlist:
            history = get_price_history(ticker, days=3)
            if not history:
                lines.append(f"➡️ `{ticker}` — no data")
                continue

            history     = sorted(history, key=lambda x: x["date"], reverse=True)
            today_data  = [e for e in history if e["date"] == today]
            prev_data   = [e for e in history if e["date"] != today]

            if not today_data:
                lines.append(f"➡️ `{ticker}` — no data today")
                continue

            current = float(today_data[0]["closing_price"])

            if prev_data:
                prev       = float(prev_data[0]["closing_price"])
                change_pct = ((current - prev) / prev) * 100
                change_abs = current - prev
                arrow      = "📈" if change_pct >= 0 else "📉"
                sign       = "+" if change_pct >= 0 else ""
                lines.append(
                    f"{arrow} `{ticker}`\n"
                    f"    ₹{prev:,.2f} → ₹{current:,.2f}\n"
                    f"    {sign}{change_abs:,.2f} ({sign}{change_pct:.2f}%)"
                )
            else:
                lines.append(f"➡️ `{ticker}` — ₹{current:,.2f}")

        try:
            req.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id":    chat_id,
                    "text":       "\n\n".join(lines),
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
        except Exception as e:
            logger.error(f"EOD failed for {chat_id}: {e}")

    logger.info(f"EOD summary sent to {len(chat_ids)} users ✅")

# =============================== NEWS UPDATE =====================

def send_news_update(label: str):
    """
    Fetch and send market news + per-stock news to all bot users.
    label = 'Morning' or 'Evening'
    """
    import os
    import requests as req
    from api.news_api import get_market_news, get_stock_news

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    # Get all users who have used the bot
    try:
        from data.database import supabase
        users_result = supabase.table("bot_users").select("chat_id").execute()
        chat_ids = [u["chat_id"] for u in users_result.data]
    except Exception as e:
        logger.error(f"Failed to fetch users for news: {e}")
        return

    if not chat_ids:
        logger.info("No users to send news to")
        return

    # ── Part 1: General market news ──
    logger.info(f"Fetching {label} market news...")
    articles = get_market_news(max_articles=10)

    if articles:
        lines = [f"📰 *{label} Market News*\n"]
        for i, a in enumerate(articles, 1):
            lines.append(
                f"{i}. [{a['title']}]({a['url']})\n"
                f"   _— {a['source']} · {a['published_at']}_"
            )
        market_message = "\n\n".join(lines)
    else:
        market_message = f"📰 *{label} Market News*\n\n_No news available right now._"

    # ── Part 2: Per stock news ──
    watchlist = get_all_watchlist_symbols()
    stock_messages = []

    # Only fetch news for actual stocks, not gold
    GOLD_TICKERS = {"GC=F", "GOLD", "XAU", "GOLD_24K", "GOLD_22K", "GOLD_18K"}
    stock_tickers = [t for t in watchlist if t.upper() not in GOLD_TICKERS]

    for ticker in stock_tickers:
        news = get_stock_news(ticker, max_articles=3)
        if not news:
            continue

        lines = [f"📌 *{ticker} News*\n"]
        for a in news:
            lines.append(
                f"• [{a['title']}]({a['url']})\n"
                f"  _— {a['source']} · {a['published_at']}_"
            )
        stock_messages.append("\n\n".join(lines))

    # ── Send to all users ──
    for chat_id in chat_ids:
        try:
            # Send general market news
            req.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id":                  chat_id,
                    "text":                     market_message,
                    "parse_mode":               "Markdown",
                    "disable_web_page_preview": True
                },
                timeout=10
            )

            # Send per-stock news
            for msg in stock_messages:
                req.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={
                        "chat_id":                  chat_id,
                        "text":                     msg,
                        "parse_mode":               "Markdown",
                        "disable_web_page_preview": True
                    },
                    timeout=10
                )

        except Exception as e:
            logger.error(f"Failed to send news to {chat_id}: {e}")

    logger.info(f"{label} news sent to {len(chat_ids)} users ✅")



# ─── Scheduler Setup ──────────────────────────────────────────
def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=IST)

    # NEWS UPDATES: Morning at 900 AM, Evening at 4:00 PM
    # ── Morning news: 9:00 AM IST ──
    scheduler.add_job(
        lambda: send_news_update("Morning"),
        trigger=CronTrigger(hour=9, minute=0, timezone=IST),
        id="news_morning",
        name="Morning news",
        replace_existing=True
    )

    # ── Evening news: 4:00 PM IST ──
    scheduler.add_job(
        lambda: send_news_update("Evening"),
        trigger=CronTrigger(hour=16, minute=0, timezone=IST),
        id="news_evening",
        name="Evening news",
        replace_existing=True
    )


    # ── Window 1: Opening (9:15–10:00) every 10 min ──
    scheduler.add_job(
        fetch_stock_prices,
        trigger=CronTrigger(
            hour="9", minute="15,25,35,45,55",
            day_of_week="mon-fri", timezone=IST
        ),
        id="stocks_opening",
        name="Stocks — opening window",
        replace_existing=True
    )

    # ── Window 2: Mid-day (10:00–14:30) every 30 min ──
    scheduler.add_job(
        fetch_stock_prices,
        trigger=CronTrigger(
            hour="10,11,12,13,14", minute="0,30",
            day_of_week="mon-fri", timezone=IST
        ),
        id="stocks_midday",
        name="Stocks — mid-day window",
        replace_existing=True
    )

    # ── Window 3: Closing (14:30–15:30) every 10 min ──
    scheduler.add_job(
        fetch_stock_prices,
        trigger=CronTrigger(
            hour="14,15", minute="40,50,0,10,20,30",
            day_of_week="mon-fri", timezone=IST
        ),
        id="stocks_closing",
        name="Stocks — closing window",
        replace_existing=True
    )

    # ── Gold: 12:00 PM IST ──
    scheduler.add_job(
        fetch_gold_price,
        trigger=CronTrigger(hour=12, minute=0, timezone=IST),
        id="gold_noon",
        name="Gold — noon",
        replace_existing=True
    )

    # ── Gold: 4:00 PM IST ──
    scheduler.add_job(
        fetch_gold_price,
        trigger=CronTrigger(hour=16, minute=0, timezone=IST),
        id="gold_evening",
        name="Gold — evening",
        replace_existing=True
    )

    # ── EOD Summary: 3:45 PM IST ──
    scheduler.add_job(
        send_eod_summary,
        trigger=CronTrigger(
            hour=15, minute=45,
            day_of_week="mon-fri", timezone=IST
        ),
        id="eod_summary",
        name="End of day summary",
        replace_existing=True
    )

    # ── Reset alert flags: 9:00 AM IST ──
    scheduler.add_job(
        reset_daily_alerts,
        trigger=CronTrigger(
            hour=9, minute=0,
            day_of_week="mon-fri", timezone=IST
        ),
        id="reset_alerts",
        name="Reset daily alert flags",
        replace_existing=True
    )

    scheduler.start()

    logger.info("Scheduler started ✅")
    logger.info("  Stocks — Opening  (9:15–10:00):  every 10 min")
    logger.info("  Stocks — Mid-day  (10:00–14:30): every 30 min")
    logger.info("  Stocks — Closing  (14:30–15:30): every 10 min")
    logger.info("  Gold        — 12:00 PM and 4:00 PM IST")
    logger.info("  EOD Summary — 3:45 PM IST daily")
    logger.info("  Alert Reset — 9:00 AM IST daily")
    logger.info("  News    — 9:00 AM and 4:00 PM IST daily")

    # Seed price history in a background thread so it doesn't block bot startup
    import threading
    threading.Thread(target=seed_price_history, daemon=True, name="seed-price-history").start()
    logger.info("Price history seeding started in background ✅")

    return scheduler