# core/alerts.py
import logging
import os
from datetime import datetime
import pytz
import requests
from data.database import (
    get_all_alert_settings, get_price_history,
    mark_alert_sent, get_watchlist
)
from api.market_api import get_price

logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")


def _get_day_open_price(ticker: str) -> float | None:
    """
    Use yesterday's closing price as today's reference point.
    This is standard practice for daily % change calculation.
    """
    history = get_price_history(ticker, days=7)
    today   = datetime.now(IST).strftime("%Y-%m-%d")

    # Find the most recent entry that is NOT today
    for entry in history:
        if entry["date"] != today:
            return float(entry["closing_price"])  # ← yesterday's close
    return None


async def _send_telegram_alert(message: str):
    """Send a message directly to your Telegram chat."""
    token   = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url     = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        requests.post(url, json={
            "chat_id":    chat_id,
            "text":       message,
            "parse_mode": "Markdown"
        }, timeout=10)
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")


# def check_and_send_alerts():
#     """
#     Called after every price fetch.
#     Checks if any stock has crossed its alert threshold
#     and sends a Telegram notification if so.
#     """
#     import asyncio

#     alert_settings = get_all_alert_settings()
#     if not alert_settings:
#         return

#     for setting in alert_settings:
#         ticker     = setting["symbol"]
#         drop_threshold  = setting.get("alert_drop")
#         rise_threshold  = setting.get("alert_rise")
#         drop_sent  = setting.get("alert_drop_sent", False)
#         rise_sent  = setting.get("alert_rise_sent", False)

#         # Skip if no alerts configured for this ticker
#         if drop_threshold is None and rise_threshold is None:
#             continue

#         # Get current price
#         result = get_price(ticker)
#         if not result:
#             continue
#         current_price = result["price"]

#         # Get today's open price to calculate % change
#         open_price = _get_day_open_price(ticker)
#         if not open_price:
#             continue

#         # Calculate % change from open
#         change_pct = ((current_price - open_price) / open_price) * 100

#         # ── Check drop alert ──
#         if (drop_threshold is not None
#                 and not drop_sent
#                 and change_pct <= -drop_threshold):

#             message = (
#                 f"🚨 *Drop Alert — {ticker}*\n\n"
#                 f"📉 Price dropped *{abs(change_pct):.2f}%* today\n"
#                 f"Open:    ₹{open_price}\n"
#                 f"Current: ₹{current_price}\n"
#                 f"Threshold: -{drop_threshold}%"
#             )
#             asyncio.run(_send_telegram_alert(message))
#             mark_alert_sent(ticker, "drop", True)
#             logger.info(f"Drop alert sent for {ticker} ({change_pct:.2f}%)")

#         # ── Check rise alert ──
#         if (rise_threshold is not None
#                 and not rise_sent
#                 and change_pct >= rise_threshold):

#             message = (
#                 f"🚀 *Rise Alert — {ticker}*\n\n"
#                 f"📈 Price rose *{change_pct:.2f}%* today\n"
#                 f"Open:    ₹{open_price}\n"
#                 f"Current: ₹{current_price}\n"
#                 f"Threshold: +{rise_threshold}%"
#             )
#             asyncio.run(_send_telegram_alert(message))
#             mark_alert_sent(ticker, "rise", True)
#             logger.info(f"Rise alert sent for {ticker} ({change_pct:.2f}%)")



def check_and_send_alerts():
    import asyncio

    alert_settings = get_all_alert_settings()
    if not alert_settings:
        logger.info("No alert settings found")
        return

    for setting in alert_settings:
        ticker          = setting["symbol"]
        drop_threshold  = setting.get("alert_drop")
        rise_threshold  = setting.get("alert_rise")
        drop_sent       = setting.get("alert_drop_sent", False)
        rise_sent       = setting.get("alert_rise_sent", False)

        if drop_threshold is None and rise_threshold is None:
            logger.info(f"{ticker}: no thresholds set — skipping")
            continue

        result = get_price(ticker)
        if not result:
            logger.warning(f"{ticker}: could not fetch price")
            continue
        current_price = result["price"]

        open_price = _get_day_open_price(ticker)
        if not open_price:
            logger.warning(f"{ticker}: no open price found — skipping")
            continue

        change_pct = ((current_price - open_price) / open_price) * 100

        # ← debug line so we can see exact numbers
        logger.info(
            f"{ticker}: open=₹{open_price}  current=₹{current_price}  "
            f"change={change_pct:.2f}%  "
            f"drop_threshold={drop_threshold}  rise_threshold={rise_threshold}  "
            f"drop_sent={drop_sent}  rise_sent={rise_sent}"
        )

        # ── Check drop alert ──
        if (drop_threshold is not None
                and not drop_sent
                and change_pct <= -float(drop_threshold)):
            message = (
                f"🚨 *Drop Alert — {ticker}*\n\n"
                f"📉 Price dropped *{abs(change_pct):.2f}%* today\n"
                f"Open:      ₹{open_price}\n"
                f"Current:   ₹{current_price}\n"
                f"Threshold: -{drop_threshold}%"
            )
            asyncio.run(_send_telegram_alert(message))
            mark_alert_sent(ticker, "drop", True)
            logger.info(f"Drop alert sent for {ticker}")
        else:
            logger.info(
                f"{ticker}: drop condition not met — "
                f"change={change_pct:.2f}% threshold=-{drop_threshold}%"
            )

        # ── Check rise alert ──
        if (rise_threshold is not None
                and not rise_sent
                and change_pct >= float(rise_threshold)):
            message = (
                f"🚀 *Rise Alert — {ticker}*\n\n"
                f"📈 Price rose *{change_pct:.2f}%* today\n"
                f"Open:      ₹{open_price}\n"
                f"Current:   ₹{current_price}\n"
                f"Threshold: +{rise_threshold}%"
            )
            asyncio.run(_send_telegram_alert(message))
            mark_alert_sent(ticker, "rise", True)
            logger.info(f"Rise alert sent for {ticker}")