# api/news_api.py
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"
TOP_HEADLINES_URL = "https://newsapi.org/v2/top-headlines"


def get_market_news(max_articles: int = 10) -> list[dict]:
    """
    Fetch top Indian stock market news.
    Returns list of { title, source, url, published_at }
    """
    if not NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not set")
        return []

    try:
        response = requests.get(
            NEWS_API_URL,
            params={
                "q":        "Indian stock market NSE BSE Sensex Nifty",
                "language": "en",
                "sortBy":   "publishedAt",
                "pageSize": max_articles,
                "apiKey":   NEWS_API_KEY,
            },
            timeout=10
        )
        response.raise_for_status()
        articles = response.json().get("articles", [])

        return [
            {
                "title":        a["title"],
                "source":       a["source"]["name"],
                "url":          a["url"],
                "published_at": a["publishedAt"][:10]  # just the date
            }
            for a in articles
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ]

    except Exception as e:
        logger.error(f"get_market_news failed: {e}")
        return []


def get_stock_news(ticker: str, max_articles: int = 3) -> list[dict]:
    """
    Fetch news for a specific stock ticker.
    Cleans the ticker to use as a search query.
    e.g. RELIANCE.NS → "Reliance"
    """
    if not NEWS_API_KEY:
        return []

    # Convert ticker to readable company name for search
    query = _ticker_to_query(ticker)

    try:
        response = requests.get(
            NEWS_API_URL,
            params={
                "q":        query,
                "language": "en",
                "sortBy":   "publishedAt",
                "pageSize": max_articles,
                "apiKey":   NEWS_API_KEY,
            },
            timeout=10
        )
        response.raise_for_status()
        articles = response.json().get("articles", [])

        return [
            {
                "title":        a["title"],
                "source":       a["source"]["name"],
                "url":          a["url"],
                "published_at": a["publishedAt"][:10]
            }
            for a in articles
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ]

    except Exception as e:
        logger.error(f"get_stock_news failed for {ticker}: {e}")
        return []


def _ticker_to_query(ticker: str) -> str:
    """
    Convert a ticker symbol to a search-friendly company name.
    RELIANCE.NS → Reliance India
    TCS.NS      → TCS Tata Consultancy
    GOLD_24K    → Gold price India
    """
    ticker = ticker.upper()

    # Known mappings
    known = {
        "RELIANCE.NS":   "Reliance Industries India",
        "RELIANCE.BO":   "Reliance Industries India",
        "TCS.NS":        "TCS Tata Consultancy Services",
        "TCS.BO":        "TCS Tata Consultancy Services",
        "INFY.NS":       "Infosys India",
        "HDFCBANK.NS":   "HDFC Bank India",
        "ICICIBANK.NS":  "ICICI Bank India",
        "TATASTEEL.NS":  "Tata Steel India",
        "WIPRO.NS":      "Wipro India",
        "ZENSARTECH.NS": "Zensar Technologies India",
        "ETERNAL.NS":    "Eternal India stock",
        "MAHSEAMLES.NS": "Maharashtra Seamless India",
        "GOLD_24K":      "Gold price India today",
        "GOLD_22K":      "Gold price India today",
        "GOLD_18K":      "Gold price India today",
        "GOLD":          "Gold price India today",
    }

    if ticker in known:
        return known[ticker]

    # Generic fallback — strip .NS/.BO and search
    clean = ticker.replace(".NS", "").replace(".BO", "").replace("_", " ")
    return f"{clean} India stock"