# bot/keyboards.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def watchlist_keyboard(ticker: str) -> InlineKeyboardMarkup:
    """
    Creates three inline buttons for each ticker in the watchlist.
    callback_data format: "action:TICKER"
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📊 Graph",
                callback_data=f"graph:{ticker}"
            ),
            InlineKeyboardButton(
                "🔔 Alert",
                callback_data=f"alert:{ticker}"
            ),
            InlineKeyboardButton(
                "🗑 Remove",
                callback_data=f"remove:{ticker}"
            ),
        ]
    ])