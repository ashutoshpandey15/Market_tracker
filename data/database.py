# data/database.py
import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ─── Connection ───────────────────────────────────────────────
def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env")
    return create_client(url, key)

supabase = get_client()  # One shared client, reused across all functions



# ─── Watchlist ────────────────────────────────────────────────
def add_symbol(symbol: str, chat_id: str) -> bool:
    """Add a symbol to a specific user's watchlist."""
    try:
        supabase.table("watchlist").insert({
            "symbol":  symbol.upper(),
            "chat_id": str(chat_id)
        }).execute()
        return True
    except Exception as e:
        logger.error(f"add_symbol failed: {e}")
        return False

def remove_symbol(symbol: str, chat_id: str) -> bool:
    """Remove a symbol from a specific user's watchlist."""
    try:
        supabase.table("watchlist")\
            .delete()\
            .eq("symbol", symbol.upper())\
            .eq("chat_id", str(chat_id))\
            .execute()
        return True
    except Exception as e:
        logger.error(f"remove_symbol failed: {e}")
        return False

def get_watchlist(chat_id: str) -> list[str]:
    """Return all symbols for a specific user."""
    try:
        result = supabase.table("watchlist")\
            .select("symbol")\
            .eq("chat_id", str(chat_id))\
            .execute()
        return [row["symbol"] for row in result.data]
    except Exception as e:
        logger.error(f"get_watchlist failed: {e}")
        return []

def get_all_watchlist_symbols() -> list[str]:
    """
    Return all unique symbols across ALL users.
    Used by scheduler to know which symbols to fetch prices for.
    """
    try:
        result = supabase.table("watchlist").select("symbol").execute()
        return list(set(row["symbol"] for row in result.data))
    except Exception as e:
        logger.error(f"get_all_watchlist_symbols failed: {e}")
        return []


# ─── Price History ────────────────────────────────────────────
def upsert_price(symbol: str, date: str, closing_price: float):
    """
    Insert a price record, or silently update it if symbol+date already exists.
    'Upsert' = Update + Insert. Prevents duplicate errors.
    """
    try:
        supabase.table("price_history").upsert(
            {
                "symbol": symbol.upper(),
                "date": date,
                "closing_price": closing_price
            },
            on_conflict="symbol,date"
        ).execute()
    except Exception as e:
        logger.error(f"upsert_price failed: {e}")

def get_price_history(symbol: str, days: int = 7) -> list[dict]:
    """
    Return the last N days of closing prices for a symbol.
    Each item is a dict: { date, closing_price }
    """
    try:
        result = (
            supabase.table("price_history")
            .select("date, closing_price")
            .eq("symbol", symbol.upper())
            .order("date", desc=True)
            .limit(days)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.error(f"get_price_history failed: {e}")
        return []


# ─── User Settings ────────────────────────────────────────────
def set_alert(symbol: str, direction: str, threshold: float):
    """
    Set an alert for a ticker.
    direction = 'drop', 'rise', or 'both'
    """
    symbol = symbol.upper()
    data = {"symbol": symbol}

    if direction in ("drop", "both"):
        data["alert_drop"] = threshold
        data["alert_drop_sent"] = False

    if direction in ("rise", "both"):
        data["alert_rise"] = threshold
        data["alert_rise_sent"] = False

    try:
        supabase.table("user_settings").upsert(
            data, on_conflict="symbol"
        ).execute()
    except Exception as e:
        logger.error(f"set_alert failed: {e}")


def get_all_alert_settings() -> list[dict]:
    """Return all rows from user_settings."""
    try:
        result = supabase.table("user_settings").select("*").execute()
        return result.data
    except Exception as e:
        logger.error(f"get_all_alert_settings failed: {e}")
        return []


def mark_alert_sent(symbol: str, direction: str, sent: bool):
    """
    Flip the alert_sent flag for a specific direction.
    direction = 'drop' or 'rise'
    Prevents repeat notifications for the same move.
    """
    column = f"alert_{direction}_sent"
    try:
        supabase.table("user_settings").update(
            {column: sent}
        ).eq("symbol", symbol.upper()).execute()
    except Exception as e:
        logger.error(f"mark_alert_sent failed: {e}")


def reset_alert_sent_flags():
    """
    Reset all alert_sent flags to False.
    Called at the start of each trading day so alerts re-arm.
    """
    try:
        supabase.table("user_settings").update({
            "alert_drop_sent": False,
            "alert_rise_sent": False
        }).neq("symbol", "").execute()
        logger.info("Alert flags reset for new day")
    except Exception as e:
        logger.error(f"reset_alert_sent_flags failed: {e}")


# ─── Analytics ────────────────────────────────────────────────
def track_user(chat_id: str, username: str, first_name: str):
    """
    Log every user who interacts with the bot.
    - New user → insert a fresh row
    - Existing user → update last_active + increment command_count
    """
    try:
        existing = supabase.table("bot_users")\
            .select("*").eq("chat_id", str(chat_id)).execute()

        if existing.data:
            supabase.table("bot_users").update({
                "last_active":   "now()",
                "username":      username or "",
                "command_count": existing.data[0]["command_count"] + 1
            }).eq("chat_id", str(chat_id)).execute()
        else:
            supabase.table("bot_users").insert({
                "chat_id":    str(chat_id),
                "username":   username or "",
                "first_name": first_name or "",
            }).execute()
            logger.info(f"New user: {first_name} (@{username})")

    except Exception as e:
        logger.error(f"track_user failed: {e}")