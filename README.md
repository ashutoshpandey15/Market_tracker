# 📈 Market Tracker Bot

A Telegram bot for tracking Indian stock market prices (NSE/BSE) and gold prices in real time — with price alerts, 7-day charts, market news, and scheduled daily summaries.

---

## Features

- **Smart search** — type a company name (e.g. `/price Reliance`) and get inline ticker buttons powered by yfinance fuzzy search; no need to know the exact symbol
- **Live prices** — NSE & BSE stocks in ₹ via yfinance; gold (24K / 22K / 18K) per 10g via GoldAPI with yfinance fallback
- **Personal watchlist** — per-user watchlist stored in Supabase; add or remove tickers anytime
- **Price alerts** — get notified when a stock drops or rises past a threshold you set
- **7-day charts** — candlestick/line charts generated with matplotlib and sent directly in chat
- **Compare stocks** — side-by-side price comparison of two tickers
- **Market news** — top headlines from NewsAPI, plus per-stock news, delivered at 9 AM and 4 PM IST
- **Daily summary** — personalised end-of-day performance report at 3:45 PM IST (Mon–Fri)
- **Scheduled price sync** — prices fetched automatically during market hours (9:15 AM – 3:30 PM IST) and saved to Supabase

---

## Commands

| Command | Description | Example |
|---|---|---|
| `/start` | Welcome message and command list | `/start` |
| `/add [ticker or name]` | Add a stock or gold to your watchlist | `/add Reliance` or `/add RELIANCE.NS` |
| `/remove [ticker or name]` | Remove from your watchlist | `/remove TCS` |
| `/watchlist` | View all your tracked stocks with live prices | `/watchlist` |
| `/price [ticker or name]` | Get the current price | `/price Infosys` |
| `/alert [ticker] [drop\|rise\|both] [%]` | Set a percentage price alert | `/alert TCS.NS drop 2.5` |
| `/graph [ticker]` | View 7-day price chart | `/graph RELIANCE.NS` |
| `/compare [ticker1] [ticker2]` | Compare two stocks side by side | `/compare RELIANCE.NS TCS.NS` |
| `/news` | Get latest market news | `/news` |
| `/stats` | Bot usage analytics (owner only) | `/stats` |

> **Ticker formats:** Use `SYMBOL.NS` for NSE, `SYMBOL.BO` for BSE, or just type the company name and pick from the search results. Use `GOLD` for 24K gold.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Bot framework | [python-telegram-bot](https://python-telegram-bot.org/) 20.7 |
| Stock data | [yfinance](https://github.com/ranaroussi/yfinance) |
| Gold prices | [GoldAPI.io](https://www.goldapi.io/) (yfinance fallback) |
| Market news | [NewsAPI](https://newsapi.org/) |
| Database | [Supabase](https://supabase.com/) (PostgreSQL) |
| Charts | matplotlib + numpy |
| Scheduler | APScheduler (BackgroundScheduler) |
| Deployment | [Railway](https://railway.app/) (Docker) |
| Language | Python 3.11 |

---

## Project Structure

```
Market_tracker/
├── main.py                  # Entry point — wires bot + scheduler
├── Dockerfile               # Docker build (handles UTF-16 requirements.txt)
├── fix_requirements.py      # Auto-converts requirements.txt encoding at build time
├── requirements.txt         # Pinned dependencies
├── railway.toml             # Railway deployment config
├── Procfile                 # Fallback start command
├── runtime.txt              # Python version hint
│
├── bot/
│   └── handlers.py          # All Telegram command & callback handlers
│
├── core/
│   ├── scheduler.py         # APScheduler jobs (price fetch, news, EOD summary)
│   ├── alerts.py            # Price alert logic
│   └── graph.py             # Chart generation (matplotlib)
│
├── api/
│   ├── market_api.py        # yfinance + GoldAPI price fetching
│   └── news_api.py          # NewsAPI integration
│
└── data/
    └── database.py          # Supabase client + all DB operations
```

---

## Environment Variables

Create a `.env` file locally (never commit it). On Railway, set these in **Project → Variables**.

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | Bot token from [@BotFather](https://t.me/BotFather) |
| `SUPABASE_URL` | ✅ | Supabase project URL (Settings → API) |
| `SUPABASE_KEY` | ✅ | Supabase anon or service key |
| `GOLD_API_KEY` | ⚠️ | [GoldAPI.io](https://www.goldapi.io/) key — falls back to yfinance if missing |
| `NEWS_API_KEY` | ⚠️ | [NewsAPI](https://newsapi.org/) key — news commands disabled if missing |
| `TELEGRAM_CHAT_ID` | ⚠️ | Your personal chat ID — required for `/stats` and owner alerts |

---
