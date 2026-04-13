# api/market_api.py
import os
import logging
import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Troy ounce to gram conversion constant
TROY_OUNCE_TO_GRAM = 31.1035

# Gold tickers we recognise
GOLD_TICKERS = {"GC=F", "GOLD", "XAU", "GOLD_24K", "GOLD_22K", "GOLD_18K"}

# Exchange suffixes
NSE_SUFFIX = ".NS"
BSE_SUFFIX = ".BO"


# ─── Main Function ────────────────────────────────────────────
def get_price(ticker: str) -> dict | None:
    """
    Fetch the latest price for a ticker.
    Always returns INR.

    Returns a dict:
    {
        "price": 1850.50,
        "currency": "INR",
        "exchange": "NSE",        ← for stocks
        "unit": "per share",      ← for stocks
        "unit": "per gram (24K)"  ← for gold
    }
    Returns None if fetch failed.
    """
    ticker = ticker.upper().strip()

    if ticker in GOLD_TICKERS:
        return _get_gold_price_inr(ticker)
    else:
        return _get_stock_price_inr(ticker)


def get_price_history_api(ticker: str, days: int = 7) -> list[dict]:
    """
    Fetch last N days of closing prices for a ticker.
    Returns: [{ "date": "2024-01-15", "closing_price": 1850.50 }, ...]
    Prices are always in INR.
    """
    ticker = ticker.upper().strip()

    if ticker in GOLD_TICKERS:
        # Gold history via yfinance GC=F then convert to INR/gram
        return _get_gold_history_inr(days)
    else:
        return _get_stock_history_inr(ticker, days)


# ─── Stock Functions ──────────────────────────────────────────
def _get_stock_price_inr(ticker: str) -> dict | None:
    """
    Fetch latest stock price.
    Automatically detects NSE (.NS) or BSE (.BO).
    If neither suffix present, tries NSE first then BSE.
    """
    try:
        # If user types "RELIANCE" without suffix, try NSE first
        if not ticker.endswith(NSE_SUFFIX) and not ticker.endswith(BSE_SUFFIX):
            ticker = ticker + NSE_SUFFIX  # default to NSE

        exchange = "BSE" if ticker.endswith(BSE_SUFFIX) else "NSE"

        data = yf.Ticker(ticker).history(period="1d")
        if data.empty:
            logger.warning(f"No data returned for {ticker}")
            return None

        price = round(float(data["Close"].iloc[-1]), 2)
        logger.info(f"{exchange}: {ticker} = ₹{price}")

        return {
            "price": price,
            "currency": "INR",
            "exchange": exchange,
            "unit": "per share"
        }

    except Exception as e:
        logger.error(f"_get_stock_price_inr failed for {ticker}: {e}")
        return None


def _get_stock_history_inr(ticker: str, days: int) -> list[dict]:
    """Fetch historical closing prices for a stock in INR."""
    try:
        if not ticker.endswith(NSE_SUFFIX) and not ticker.endswith(BSE_SUFFIX):
            ticker = ticker + NSE_SUFFIX

        data = yf.Ticker(ticker).history(period=f"{days}d")
        if data.empty:
            return []

        return [
            {
                "date": str(date.date()),
                "closing_price": round(float(row["Close"]), 2)
            }
            for date, row in data.iterrows()
        ]

    except Exception as e:
        logger.error(f"_get_stock_history_inr failed for {ticker}: {e}")
        return []


# ─── Gold Functions ───────────────────────────────────────────
def _get_gold_price_inr(ticker: str = "GOLD_24K") -> dict | None:
    """
    Fetch gold price in INR per 10g.
    ticker determines which karat to return.
    """
    api_key = os.getenv("GOLD_API_KEY")

    if api_key:
        try:
            response = requests.get(
                "https://www.goldapi.io/api/XAU/INR",
                headers={"x-access-token": api_key},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Map ticker to correct karat field
            karat_map = {
                "GOLD":     ("price_gram_24k", "24K"),
                "GOLD_24K": ("price_gram_24k", "24K"),
                "GOLD_22K": ("price_gram_22k", "22K"),
                "GOLD_18K": ("price_gram_18k", "18K"),
                "GC=F":     ("price_gram_24k", "24K"),
                "XAU":      ("price_gram_24k", "24K"),
            }
            field, label = karat_map.get(ticker.upper(), ("price_gram_24k", "24K"))
            price_per_10g = round(float(data[field]) * 10, 2)

            result = {
                "price":      price_per_10g,
                "currency":   "INR",
                "exchange":   "IDC",
                "unit":       f"per 10g ({label})",
                "change_pct": round(float(data["chp"]), 2),
            }

            set_cache(ticker.upper(), result)
            logger.info(f"GoldAPI: {ticker} = ₹{price_per_10g}/10g")
            return result

        except Exception as e:
            logger.error(f"GoldAPI failed: {e}, falling back to yfinance")

    return _get_gold_price_via_yfinance(ticker)


def _get_gold_price_via_yfinance(ticker: str = "GOLD_24K") -> dict | None:
    """Fallback gold price using yfinance + USDINR conversion."""
    try:
        gold_data = yf.Ticker("GC=F").history(period="1d")
        inr_data  = yf.Ticker("USDINR=X").history(period="1d")

        if gold_data.empty or inr_data.empty:
            return None

        gold_usd_per_oz = float(gold_data["Close"].iloc[-1])
        usd_to_inr      = float(inr_data["Close"].iloc[-1])

        # Karat purity multipliers
        purity_map = {
            "GOLD":     (1.0,    "24K"),
            "GOLD_24K": (1.0,    "24K"),
            "GOLD_22K": (0.9167, "22K"),
            "GOLD_18K": (0.75,   "18K"),
            "GC=F":     (1.0,    "24K"),
            "XAU":      (1.0,    "24K"),
        }
        purity, label = purity_map.get(ticker.upper(), (1.0, "24K"))

        price_per_10g = round(
            (gold_usd_per_oz * usd_to_inr / TROY_OUNCE_TO_GRAM) * 10 * purity, 2
        )

        return {
            "price":    price_per_10g,
            "currency": "INR",
            "exchange": "FOREX (yfinance)",
            "unit":     f"per 10g ({label})",
        }

    except Exception as e:
        logger.error(f"_get_gold_price_via_yfinance failed: {e}")
        return None


def _get_gold_history_inr(days: int) -> list[dict]:
    """
    Fetch historical gold prices in INR per gram using yfinance.
    Uses GC=F (USD) × USDINR=X rate ÷ 31.1035.
    """
    try:
        gold_data = yf.Ticker("GC=F").history(period=f"{days}d")
        inr_data  = yf.Ticker("USDINR=X").history(period=f"{days}d")

        if gold_data.empty or inr_data.empty:
            return []

        result = []
        for date, row in gold_data.iterrows():
            date_str = str(date.date())
            # Find matching INR rate for this date
            matching = inr_data[inr_data.index.date == date.date()]
            if matching.empty:
                continue
            usd_to_inr = float(matching["Close"].iloc[-1])
            price_inr_gram = round(
                (float(row["Close"]) * usd_to_inr) / TROY_OUNCE_TO_GRAM * 10, 2
            )
            result.append({"date": date_str, "closing_price": price_inr_gram})

        return result

    except Exception as e:
        logger.error(f"_get_gold_history_inr failed: {e}")
        return []




if __name__ == "__main__":
    print("RELIANCE (NSE):", get_price("RELIANCE.NS"))
    print("TCS (NSE):     ", get_price("TCS.NS"))
    print("RELIANCE (BSE):", get_price("RELIANCE.BO"))
    print("Gold:          ", get_price("GOLD"))
    print("Gold history:  ", get_price_history_api("GOLD", days=3))