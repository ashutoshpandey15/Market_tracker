# # bot/handlers.py
# import logging
# import os
# from telegram import Update
# from telegram.ext import ContextTypes
# from telegram.ext import MessageHandler, filters
# import yfinance as yf

# from data.database import (
#     add_symbol, remove_symbol, get_watchlist,
#     get_price_history, set_alert,
#     get_all_alert_settings
# )
# from api.market_api import get_price

# logger = logging.getLogger(__name__)

# # ─── Analytics Helper ─────────────────────────────────────────
# def _track(update: Update):
#     """
#     Call at the start of every command handler.
#     Silently logs the user — never blocks the command.
#     """
#     try:
#         from data.database import track_user
#         user = update.effective_user
#         track_user(
#             chat_id    = str(update.effective_chat.id),
#             username   = user.username   or "",
#             first_name = user.first_name or ""
#         )
#     except Exception:
#         pass  # analytics should never crash the bot


# # ─── /stats ───────────────────────────────────────────────────
# # async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
# #     """Show bot usage analytics. Only works for the bot owner."""
# #     _track(update)

# #     # Only you can see stats
# #     owner_chat_id = os.getenv("TELEGRAM_CHAT_ID")
# #     if str(update.effective_chat.id) != str(owner_chat_id):
# #         await update.message.reply_text(
# #             "⚠️ This command is only available to the bot owner."
# #         )
# #         return

# #     try:
# #         from data.database import supabase
# #         result = supabase.table("bot_users").select("*").execute()
# #         users  = result.data

# #         if not users:
# #             await update.message.reply_text("No users yet.")
# #             return

# #         total_users    = len(users)
# #         total_commands = sum(u["command_count"] for u in users)

# #         # Most active users
# #         top_users = sorted(users, key=lambda u: u["command_count"], reverse=True)[:5]
# #         top_lines = "\n".join([
# #             f"  {i+1}. {u['first_name']} (@{u['username']}) "
# #             f"— {u['command_count']} commands"
# #             for i, u in enumerate(top_users)
# #         ])

# #         await update.message.reply_text(
# #             f"📊 *Bot Analytics*\n\n"
# #             f"👥 Total users:    *{total_users}*\n"
# #             f"⚡ Total commands: *{total_commands}*\n\n"
# #             f"🏆 *Most Active Users:*\n{top_lines}",
# #             parse_mode="Markdown"
# #         )

# #     except Exception as e:
# #         await update.message.reply_text(f"❌ Failed to fetch stats: {e}")

# async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     _track(update)

#     owner_chat_id = os.getenv("TELEGRAM_CHAT_ID")
#     if str(update.effective_chat.id) != str(owner_chat_id):
#         await update.message.reply_text(
#             "⚠️ This command is only available to the bot owner."
#         )
#         return

#     try:
#         from data.database import supabase
#         result = supabase.table("bot_users").select("*").execute()
#         users  = result.data

#         if not users:
#             await update.message.reply_text("No users yet.")
#             return

#         total_users    = len(users)
#         total_commands = sum(u["command_count"] for u in users)

#         top_users = sorted(
#             users,
#             key=lambda u: u["command_count"],
#             reverse=True
#         )[:5]

#         # ← Fix: don't use Markdown for usernames
#         # plain text avoids all parse errors
#         top_lines = "\n".join([
#             f"  {i+1}. {u['first_name']} "
#             f"({u['command_count']} commands)"
#             for i, u in enumerate(top_users)
#         ])

#         # Send as plain text — no parse_mode
#         await update.message.reply_text(
#             f"📊 Bot Analytics\n\n"
#             f"👥 Total users:    {total_users}\n"
#             f"⚡ Total commands: {total_commands}\n\n"
#             f"🏆 Most Active Users:\n{top_lines}"
#             # ← no parse_mode here
#         )

#     except Exception as e:
#         await update.message.reply_text(f"❌ Failed to fetch stats: {e}")



# # ─── General Message Handler ──────────────────────────────────
# async def general_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     _track(update)
#     """Responds to casual messages like 'hi', 'hello' etc."""
#     text = update.message.text.lower().strip()

#     greetings = {"hi", "hello", "hey", "hii", "helo", "namaste"}

#     if any(word in text for word in greetings):
#         await update.message.reply_text(
#             "👋 Hey! I'm *Market Price Tracker Bot*\n\n"
#             "I help you track Indian stocks and gold prices in real time.\n\n"
#             "📈 *What I can do:*\n"
#             "• Track NSE/BSE stocks in ₹\n"
#             "• Track Gold prices per 10g in ₹\n"
#             "• Alert you on price drops or rises\n"
#             "• Send daily market summary at 3:45 PM\n"
#             "• Show 7-day price charts\n\n"
#             "⚡ *Commands:*\n"
#             "/add `TICKER` — Add stock to watchlist\n"
#             "/remove `TICKER` — Remove stock\n"
#             "/watchlist — View all tracked stocks\n"
#             "/price `TICKER` — Get current price\n"
#             "/alert `TICKER` drop/rise/both `%` — Set alert\n"
#             "/graph `TICKER` — View 7-day chart\n"
#             "/compare `TICKER1` `TICKER2` — Compare two stocks\n"
#             "/news — Get latest market news\n"
#             "/stats — Show bot usage analytics\n\n"
#             "💡 *Examples:*\n"
#             "`/add RELIANCE.NS`\n"
#             "`/add GOLD`\n"
#             "`/alert TCS.NS drop 2.0`"
#             "`/compare RELIANCE.NS TCS.NS`\n",
#             parse_mode="Markdown"
#         )
#     else:
#         await update.message.reply_text(
#             "🤖 I only understand commands. Type `/start` to see what I can do!",
#             parse_mode="Markdown"
#         )


# # ─── /start ───────────────────────────────────────────────────
# async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Welcome message shown when user first opens the bot."""
#     _track(update)
#     await update.message.reply_text(
#         "👋 Welcome to *Market Tracker Bot!*\n\n"
#         "Here's what I can do:\n\n"
#         "📈 `/add TICKER` — Add a stock to your watchlist\n"
#         "🗑 `/remove TICKER` — Remove a stock\n"
#         "📋 `/watchlist` — View all tracked stocks\n"
#         "💰 `/price TICKER` — Get current price\n"
#         "🔔 `/alert TICKER 2.5` — Alert if price drops 2.5%\n"
#         "📊 `/news` — Get latest market news\n"
#         "📊 `/graph TICKER` — View 7-day price chart\n"
#         "🔴compare `TICKER1` `TICKER2` — Compare two stocks\n\n"
#         "_Examples:_\n"
#         "`/add RELIANCE.NS`\n"
#         "`/add TCS.NS`\n"
#         "`/add GOLD`\n"
#         "`/price INFY.NS`\n"
#         "`/compare RELIANCE.NS TCS.NS`\n"
#         "`/alert RELIANCE.NS 2.0`",
#         parse_mode="Markdown"
#     )


# # ─── /add ─────────────────────────────────────────────────────
# # async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
# #     _track(update)
# #     chat_id = str(update.effective_chat.id)
# #     if not context.args:
# #         await update.message.reply_text(
# #             "⚠️ Please provide a ticker.\n"
# #             "Example: `/add RELIANCE.NS`",
# #             parse_mode="Markdown"
# #         )
# #         return

# #     ticker = context.args[0].upper().strip()

# #     # Special handling — if user types just GOLD, guide them
# #     if ticker == "GOLD":
# #         await update.message.reply_text(
# #             "🥇 *Which gold karat would you like to track?*\n\n"
# #             "`/add GOLD_24K` — 24K (pure gold, investment)\n"
# #             "`/add GOLD_22K` — 22K (jewellery standard)\n"
# #             "`/add GOLD_18K` — 18K (studded jewellery)\n\n"
# #             "_You can add multiple karats to your watchlist!_",
# #             parse_mode="Markdown"
# #         )
# #         return

# #     await update.message.reply_text(
# #         f"🔍 Checking `{ticker}`...", parse_mode="Markdown"
# #     )

# #     GOLD_TICKERS = {"GC=F", "GOLD_24K", "GOLD_22K", "GOLD_18K", "XAU"}
# #     if ticker not in GOLD_TICKERS:
# #         data = yf.Ticker(ticker).history(period="1d")
# #         if data.empty:
# #             await update.message.reply_text(
# #                 f"❌ `{ticker}` doesn't exist or has no data.\n\n"
# #                 f"💡 Tips:\n"
# #                 f"• NSE stocks: add `.NS` → `RELIANCE.NS`\n"
# #                 f"• BSE stocks: add `.BO` → `RELIANCE.BO`\n"
# #                 f"• Gold: use `GOLD_24K`, `GOLD_22K`, or `GOLD_18K`",
# #                 parse_mode="Markdown"
# #             )
# #             return

# #     success = add_symbol(ticker, chat_id)
# #     if not success:
# #         await update.message.reply_text(
# #             f"⚠️ `{ticker}` is already in your watchlist.",
# #             parse_mode="Markdown"
# #         )
# #         return

# #     result = get_price(ticker)
# #     if result:
# #         await update.message.reply_text(
# #             f"✅ `{ticker}` added to your watchlist!\n\n"
# #             f"💰 Current price: *₹{result['price']}* {result['unit']}\n"
# #             f"🏦 Exchange: {result['exchange']}",
# #             parse_mode="Markdown"
# #         )
# #     else:
# #         await update.message.reply_text(
# #             f"✅ `{ticker}` added!\n"
# #             f"_(Price will be fetched on next scheduler run)_",
# #             parse_mode="Markdown"
# #         )

# async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     _track(update)
#     chat_id = str(update.effective_chat.id)

#     if not context.args:
#         await update.message.reply_text(
#             "⚠️ Please provide a stock name or ticker.\n"
#             "Examples:\n"
#             "`/add reliance`\n"
#             "`/add RELIANCE.NS`\n"
#             "`/add GOLD_24K`",
#             parse_mode="Markdown"
#         )
#         return

#     query  = context.args[0].strip()
#     ticker = query.upper()

#     # ── Gold shortcut ──
#     if ticker == "GOLD":
#         await update.message.reply_text(
#             "🥇 *Which gold karat would you like to track?*\n\n"
#             "`/add GOLD_24K` — 24K (pure gold, investment)\n"
#             "`/add GOLD_22K` — 22K (jewellery standard)\n"
#             "`/add GOLD_18K` — 18K (studded jewellery)\n\n"
#             "_You can add multiple karats!_",
#             parse_mode="Markdown"
#         )
#         return

#     GOLD_TICKERS = {"GC=F", "GOLD_24K", "GOLD_22K", "GOLD_18K", "XAU"}

#     # ── If exact ticker format provided (has . or _) → add directly ──
#     if "." in ticker or "_" in ticker or ticker in GOLD_TICKERS:
#         await _add_ticker_directly(update, ticker, chat_id)
#         return

#     # ── Fuzzy search — user typed a name like "reliance" ──
#     await update.message.reply_text(
#         f"🔍 Searching for *{query}*...",
#         parse_mode="Markdown"
#     )

#     try:
#         import yfinance as yf
#         search_results = yf.Search(query, max_results=6).quotes
#     except Exception as e:
#         logger.error(f"yfinance search failed: {e}")
#         search_results = []

#     if not search_results:
#         await update.message.reply_text(
#             f"❌ No results found for *{query}*.\n\n"
#             f"Try using the exact ticker:\n"
#             f"`/add RELIANCE.NS` for NSE\n"
#             f"`/add RELIANCE.BO` for BSE",
#             parse_mode="Markdown"
#         )
#         return

#     # Filter to Indian stocks (.NS, .BO) and limit to 6
#     indian = [
#         r for r in search_results
#         if r.get("symbol", "").endswith((".NS", ".BO"))
#     ][:6]

#     # If no Indian results, show all results
#     if not indian:
#         indian = search_results[:6]

#     if not indian:
#         await update.message.reply_text(
#             f"❌ No Indian stocks found for *{query}*.\n"
#             f"Try `/add RELIANCE.NS` directly.",
#             parse_mode="Markdown"
#         )
#         return

#     # Build inline buttons — one per result
#     from telegram import InlineKeyboardButton, InlineKeyboardMarkup

#     buttons = []
#     for r in indian:
#         symbol      = r.get("symbol", "")
#         name        = r.get("shortname") or r.get("longname") or symbol
#         exchange    = "NSE" if symbol.endswith(".NS") else \
#                       "BSE" if symbol.endswith(".BO") else "INT"
#         button_text = f"{symbol} — {exchange}"
#         buttons.append([
#             InlineKeyboardButton(
#                 button_text,
#                 callback_data=f"addticker:{symbol}"
#             )
#         ])

#     await update.message.reply_text(
#         f"🔍 *Results for '{query}':*\n\nTap to add:",
#         parse_mode="Markdown",
#         reply_markup=InlineKeyboardMarkup(buttons)
#     )


# async def _add_ticker_directly(update, ticker, chat_id):
#     """Add a ticker directly without fuzzy search."""
#     GOLD_TICKERS = {"GC=F", "GOLD_24K", "GOLD_22K", "GOLD_18K", "XAU"}

#     await update.message.reply_text(
#         f"🔍 Checking `{ticker}`...",
#         parse_mode="Markdown"
#     )

#     if ticker not in GOLD_TICKERS:
#         import yfinance as yf
#         data = yf.Ticker(ticker).history(period="1d")
#         if data.empty:
#             await update.message.reply_text(
#                 f"❌ `{ticker}` doesn't exist or has no data.\n\n"
#                 f"💡 Tips:\n"
#                 f"• NSE stocks: add `.NS` → `RELIANCE.NS`\n"
#                 f"• BSE stocks: add `.BO` → `RELIANCE.BO`\n"
#                 f"• Gold: use `GOLD_24K`, `GOLD_22K`, or `GOLD_18K`",
#                 parse_mode="Markdown"
#             )
#             return

#     success = add_symbol(ticker, chat_id)
#     if not success:
#         await update.message.reply_text(
#             f"⚠️ `{ticker}` is already in your watchlist.",
#             parse_mode="Markdown"
#         )
#         return

#     from api.market_api import get_price
#     result = get_price(ticker)
#     if result:
#         await update.message.reply_text(
#             f"✅ `{ticker}` added to your watchlist!\n\n"
#             f"💰 Current price: *₹{result['price']}* {result['unit']}\n"
#             f"🏦 Exchange: {result['exchange']}",
#             parse_mode="Markdown"
#         )
#     else:
#         await update.message.reply_text(
#             f"✅ `{ticker}` added!\n"
#             f"_(Price fetched on next scheduler run)_",
#             parse_mode="Markdown"
#         )





# # ─── /remove ──────────────────────────────────────────────────
# async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Remove a stock from the watchlist.
#     Usage: /remove RELIANCE.NS
#     """
#     _track(update)
#     chat_id = str(update.effective_chat.id)
#     if not context.args:
#         await update.message.reply_text(
#             "⚠️ Please provide a ticker.\n"
#             "Example: `/remove RELIANCE.NS`",
#             parse_mode="Markdown"
#         )
#         return

#     ticker = context.args[0].upper().strip()

#     # Check it's actually in the user's watchlist first
#     watchlist = get_watchlist(chat_id)
#     if ticker not in watchlist:
#         await update.message.reply_text(
#             f"⚠️ `{ticker}` is not in your watchlist.",
#             parse_mode="Markdown"
#         )
#         return

#     remove_symbol(ticker, chat_id)
#     await update.message.reply_text(
#         f"🗑 `{ticker}` removed from your watchlist.",
#         parse_mode="Markdown"
#     )

# # ─── /watchlist Phase 1 code ───────────────────────────────────────────────
# # async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
# #     """Show all tracked stocks with their latest prices."""
# #     watchlist = get_watchlist()

# #     if not watchlist:
# #         await update.message.reply_text(
# #             "📋 Your watchlist is empty.\n\n"
# #             "Add stocks with `/add RELIANCE.NS`",
# #             parse_mode="Markdown"
# #         )
# #         return

# #     await update.message.reply_text("⏳ Fetching latest prices...")

# #     lines = ["📋 *Your Watchlist*\n"]
# #     for ticker in watchlist:
# #         result = get_price(ticker)
# #         if result:
# #             lines.append(
# #                 f"• `{ticker}` — *₹{result['price']}* {result['unit']}"
# #             )
# #         else:
# #             lines.append(f"• `{ticker}` — _price unavailable_")

# #     await update.message.reply_text(
# #         "\n".join(lines),
# #         parse_mode="Markdown"
# #     )

# # ─── /watchlist Phase 2 Improved ───────────────────────────────────────────────
# async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Show all tracked stocks with live prices and inline action buttons.
#     Each stock gets its own message with [Graph] [Alert] [Remove] buttons.
#     """
#     _track(update)
#     chat_id = str(update.effective_chat.id)
#     watchlist = get_watchlist(chat_id)

#     if not watchlist:
#         await update.message.reply_text(
#             "📋 Your watchlist is empty.\n\n"
#             "Add stocks with `/add RELIANCE.NS`",
#             parse_mode="Markdown"
#         )
#         return

#     await update.message.reply_text("⏳ Fetching latest prices...")

#     from bot.keyboards import watchlist_keyboard

#     for ticker in watchlist:
#         result = get_price(ticker)

#         if result:
#             price_line = f"💰 *₹{result['price']}* {result['unit']}"
#             exchange   = f"🏦 {result['exchange']}"
#         else:
#             price_line = "💰 _price unavailable_"
#             exchange   = ""

#         # Each stock is its own message with buttons below it
#         await update.message.reply_text(
#             f"📌 *{ticker}*\n{price_line}\n{exchange}",
#             parse_mode="Markdown",
#             reply_markup=watchlist_keyboard(ticker)
#         )

# # ─── Inline Button Callbacks ───────────────────────────────────
# # async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
# #     """
# #     Handles all inline button taps from the watchlist.
# #     Parses callback_data in format "action:TICKER"
# #     """
# #     query  = update.callback_query
# #     await query.answer()  # ← removes the loading spinner on the button

# #     # Parse the callback data
# #     parts  = query.data.split(":", 1)
# #     if len(parts) != 2:
# #         return

# #     action, ticker = parts[0], parts[1]

# #     # ── Graph button ──────────────────────────────────────────
# #     if action == "graph":
# #         await query.message.reply_text(
# #             f"📊 Generating chart for `{ticker}`...",
# #             parse_mode="Markdown"
# #         )

# #         from data.database import get_price_history
# #         from core.graph import generate_price_chart
# #         import os

# #         history = get_price_history(ticker, days=7)

# #         if not history or len(history) < 2:
# #             await query.message.reply_text(
# #                 f"⚠️ Not enough price history for `{ticker}` yet.\n"
# #                 f"Check back tomorrow!",
# #                 parse_mode="Markdown"
# #             )
# #             return

# #         chart_path = generate_price_chart(ticker, history)
# #         if not chart_path:
# #             await query.message.reply_text(
# #                 f"❌ Failed to generate chart for `{ticker}`."
# #             )
# #             return

# #         try:
# #             with open(chart_path, "rb") as photo:
# #                 await query.message.reply_photo(
# #                     photo=photo,
# #                     caption=(
# #                         f"📊 *{ticker}* — Last {len(history)} days\n"
# #                         f"Latest: *₹{history[0]['closing_price']}*"
# #                     ),
# #                     parse_mode="Markdown"
# #                 )
# #         finally:
# #             if os.path.exists(chart_path):
# #                 os.remove(chart_path)

# #     # ── Remove button ─────────────────────────────────────────
# #     elif action == "remove":
# #         from data.database import remove_symbol
# #         chat_id = str(query.message.chat.id)
# #         remove_symbol(ticker, chat_id)

# #         # Edit the original message to show it's been removed
# #         # instead of sending a new message
# #         await query.edit_message_text(
# #             f"🗑 *{ticker}* removed from your watchlist.",
# #             parse_mode="Markdown"
# #         )

# #     # ── Alert button ──────────────────────────────────────────
# #     elif action == "alert":
# #         await query.message.reply_text(
# #             f"🔔 *Set Alert for {ticker}*\n\n"
# #             f"Use the command:\n"
# #             f"`/alert {ticker} drop 2.0` — notify if drops 2%\n"
# #             f"`/alert {ticker} rise 3.0` — notify if rises 3%\n"
# #             f"`/alert {ticker} both 2.0` — notify either way\n\n"
# #             f"_Replace `2.0` with your desired percentage._",
# #             parse_mode="Markdown"
# #         )

# async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()

#     parts = query.data.split(":", 1)
#     if len(parts) != 2:
#         return

#     action, ticker = parts[0], parts[1]
#     chat_id = str(update.effective_chat.id)

#     # ── Add ticker from fuzzy search result ──
#     if action == "addticker":
#         await _add_ticker_directly(query.message, ticker, chat_id)
#         return

#     # ── Graph button ──
#     if action == "graph":
#         await query.message.reply_text(
#             f"📊 Generating chart for `{ticker}`...",
#             parse_mode="Markdown"
#         )
#         from data.database import get_price_history
#         from core.graph import generate_price_chart
#         import os

#         history = get_price_history(ticker, days=7)
#         if not history or len(history) < 2:
#             await query.message.reply_text(
#                 f"⚠️ Not enough price history for `{ticker}` yet.",
#                 parse_mode="Markdown"
#             )
#             return

#         chart_path = generate_price_chart(ticker, history)
#         if not chart_path:
#             await query.message.reply_text(f"❌ Failed to generate chart.")
#             return

#         try:
#             with open(chart_path, "rb") as photo:
#                 await query.message.reply_photo(
#                     photo=photo,
#                     caption=(
#                         f"📊 *{ticker}* — Last {len(history)} days\n"
#                         f"Latest: *₹{history[0]['closing_price']}*"
#                     ),
#                     parse_mode="Markdown"
#                 )
#         finally:
#             if os.path.exists(chart_path):
#                 os.remove(chart_path)

#     # ── Remove button ──
#     elif action == "remove":
#         from data.database import remove_symbol
#         remove_symbol(ticker, chat_id)
#         await query.edit_message_text(
#             f"🗑 {ticker} removed from your watchlist."
#         )

#     # ── Alert button ──
#     elif action == "alert":
#         await query.message.reply_text(
#             f"🔔 Set Alert for {ticker}\n\n"
#             f"Use the command:\n"
#             f"/alert {ticker} drop 2.0\n"
#             f"/alert {ticker} rise 3.0\n"
#             f"/alert {ticker} both 2.0"
#         )



# # ─── /price ───────────────────────────────────────────────────
# async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Get the current price of any stock instantly.
#     Usage: /price TCS.NS
#     """
#     _track(update)
#     if not context.args:
#         await update.message.reply_text(
#             "⚠️ Please provide a ticker.\n"
#             "Example: `/price TCS.NS`",
#             parse_mode="Markdown"
#         )
#         return

#     ticker = context.args[0].upper().strip()
#     result = get_price(ticker)

#     if not result:
#         await update.message.reply_text(
#             f"❌ Could not fetch price for `{ticker}`.\n"
#             f"Make sure the ticker is valid.",
#             parse_mode="Markdown"
#         )
#         return

#     await update.message.reply_text(
#         f"💰 *{ticker}*\n\n"
#         f"Price:    *₹{result['price']}* {result['unit']}\n"
#         f"Exchange: {result['exchange']}",
#         parse_mode="Markdown"
#     )


# # ─── /alert ───────────────────────────────────────────────────
# async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Set a price alert for a stock.
#     Usage:
#       /alert RELIANCE.NS drop 2.0
#       /alert RELIANCE.NS rise 3.0
#       /alert RELIANCE.NS both 2.0
#     """
#     _track(update)
#     chat_id = str(update.effective_chat.id)

#     if len(context.args) < 3:
#         await update.message.reply_text(
#             "⚠️ Usage:\n"
#             "`/alert TICKER drop 2.0`\n"
#             "`/alert TICKER rise 3.0`\n"
#             "`/alert TICKER both 2.0`\n\n"
#             "_Examples:_\n"
#             "`/alert RELIANCE.NS drop 2.0` — notify if drops 2%\n"
#             "`/alert TCS.NS rise 3.0` — notify if rises 3%\n"
#             "`/alert GOLD both 1.5` — notify if moves 1.5% either way",
#             parse_mode="Markdown"
#         )
#         return

#     ticker    = context.args[0].upper().strip()
#     direction = context.args[1].lower().strip()

#     # Validate direction
#     if direction not in ("drop", "rise", "both"):
#         await update.message.reply_text(
#             "⚠️ Direction must be `drop`, `rise`, or `both`.\n"
#             "Example: `/alert RELIANCE.NS drop 2.0`",
#             parse_mode="Markdown"
#         )
#         return

#     # Validate threshold
#     try:
#         threshold = float(context.args[2])
#         if threshold <= 0 or threshold > 100:
#             raise ValueError
#     except ValueError:
#         await update.message.reply_text(
#             "⚠️ Please provide a valid percentage between 0 and 100.\n"
#             "Example: `/alert RELIANCE.NS drop 2.5`",
#             parse_mode="Markdown"
#         )
#         return

#     # Check ticker is in watchlist
#     watchlist = get_watchlist(chat_id)
#     if ticker not in watchlist:
#         await update.message.reply_text(
#             f"⚠️ `{ticker}` is not in your watchlist.\n"
#             f"Add it first with `/add {ticker}`",
#             parse_mode="Markdown"
#         )
#         return

#     set_alert(ticker, direction, threshold)

#     # Build a clear confirmation message
#     if direction == "drop":
#         detail = f"📉 Notify if drops more than *{threshold}%*"
#     elif direction == "rise":
#         detail = f"📈 Notify if rises more than *{threshold}%*"
#     else:
#         detail = f"📉📈 Notify if moves more than *{threshold}%* either way"

#     await update.message.reply_text(
#         f"🔔 Alert set for `{ticker}`!\n\n{detail}",
#         parse_mode="Markdown"
#     )



# # ─── /graph ───────────────────────────────────────────────────
# async def graph_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     /graph RELIANCE.NS       → single stock chart
#     /graph GOLD_24K          → single karat chart
#     /graph GOLD compare      → 24K vs 22K comparison chart
#     """
#     _track(update)
#     chat_id = str(update.effective_chat.id)
#     if not context.args:
#         await update.message.reply_text(
#             "⚠️ Please provide a ticker.\n"
#             "Examples:\n"
#             "`/graph RELIANCE.NS`\n"
#             "`/graph GOLD_24K`\n"
#             "`/graph GOLD compare`",
#             parse_mode="Markdown"
#         )
#         return

#     from data.database import get_price_history
#     from core.graph import generate_price_chart, generate_gold_comparison_chart
#     import os

#     ticker = context.args[0].upper().strip()

#     # ── Special case: /graph GOLD compare ──
#     if ticker == "GOLD" and len(context.args) > 1 and context.args[1].lower() == "compare":
#         await update.message.reply_text("📊 Generating gold comparison chart...")

#         histories = {
#             "GOLD_24K": get_price_history("GOLD_24K", days=7),
#             "GOLD_22K": get_price_history("GOLD_22K", days=7),
#         }

#         if all(len(h) < 2 for h in histories.values()):
#             await update.message.reply_text(
#                 "⚠️ Not enough price history yet.\n"
#                 "Add `GOLD_24K` and `GOLD_22K` to your watchlist first.",
#                 parse_mode="Markdown"
#             )
#             return

#         chart_path = generate_gold_comparison_chart(histories)
#         if not chart_path:
#             await update.message.reply_text("❌ Failed to generate comparison chart.")
#             return

#         try:
#             with open(chart_path, "rb") as photo:
#                 await update.message.reply_photo(
#                     photo=photo,
#                     caption="📊 *Gold Comparison — 24K vs 22K*\nper 10g in ₹",
#                     parse_mode="Markdown"
#                 )
#         finally:
#             if os.path.exists(chart_path):
#                 os.remove(chart_path)
#         return

#     # ── Single ticker chart ──
#     watchlist = get_watchlist(chat_id)
#     if ticker not in watchlist:
#         await update.message.reply_text(
#             f"⚠️ `{ticker}` is not in your watchlist.\n"
#             f"Add it first with `/add {ticker}`",
#             parse_mode="Markdown"
#         )
#         return

#     await update.message.reply_text(
#         f"📊 Generating chart for `{ticker}`...",
#         parse_mode="Markdown"
#     )

#     history = get_price_history(ticker, days=7)

#     if not history or len(history) < 2:
#         await update.message.reply_text(
#             f"⚠️ Not enough price history for `{ticker}` yet.\n"
#             f"Check back tomorrow!",
#             parse_mode="Markdown"
#         )
#         return

#     chart_path = generate_price_chart(ticker, history)
#     if not chart_path:
#         await update.message.reply_text(
#             f"❌ Failed to generate chart for `{ticker}`.",
#             parse_mode="Markdown"
#         )
#         return

#     try:
#         with open(chart_path, "rb") as photo:
#             await update.message.reply_photo(
#                 photo=photo,
#                 caption=(
#                     f"📊 *{ticker}* — Last {len(history)} days\n"
#                     f"Latest: *₹{history[0]['closing_price']}*"
#                 ),
#                 parse_mode="Markdown"
#             )
#     finally:
#         if os.path.exists(chart_path):
#             os.remove(chart_path)
#             logger.info(f"Temp chart deleted: {chart_path}")


# # ─── /compare ─────────────────────────────────────────────────
# async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Compare two tickers on the same chart.
#     Usage:
#       /compare RELIANCE.NS TCS.NS
#       /compare GOLD_24K GOLD_22K
#     """
#     _track(update)
#     chat_id = str(update.effective_chat.id)
#     if len(context.args) < 2:
#         await update.message.reply_text(
#             "⚠️ Please provide two tickers.\n\n"
#             "Examples:\n"
#             "`/compare RELIANCE.NS TCS.NS`\n"
#             "`/compare GOLD_24K GOLD_22K`",
#             parse_mode="Markdown"
#         )
#         return

#     ticker1 = context.args[0].upper().strip()
#     ticker2 = context.args[1].upper().strip()

#     if ticker1 == ticker2:
#         await update.message.reply_text(
#             "⚠️ Please provide two *different* tickers.",
#             parse_mode="Markdown"
#         )
#         return

#     await update.message.reply_text(
#         f"📊 Comparing `{ticker1}` vs `{ticker2}`...",
#         parse_mode="Markdown"
#     )

#     from data.database import get_price_history
#     from api.market_api import get_price_history_api
#     from core.graph import generate_comparison_chart
#     import os

#     # Try DB first, fall back to live API fetch if not enough data
#     history1 = get_price_history(ticker1, days=7)
#     history2 = get_price_history(ticker2, days=7)

#     if len(history1) < 2:
#         await update.message.reply_text(
#             f"⏳ Fetching history for `{ticker1}`...",
#             parse_mode="Markdown"
#         )
#         history1 = get_price_history_api(ticker1, days=7)
#         # Save to DB for future use
#         from data.database import upsert_price
#         for entry in history1:
#             upsert_price(ticker1, entry["date"], entry["closing_price"])

#     if len(history2) < 2:
#         await update.message.reply_text(
#             f"⏳ Fetching history for `{ticker2}`...",
#             parse_mode="Markdown"
#         )
#         history2 = get_price_history_api(ticker2, days=7)
#         from data.database import upsert_price
#         for entry in history2:
#             upsert_price(ticker2, entry["date"], entry["closing_price"])

#     if len(history1) < 2 or len(history2) < 2:
#         await update.message.reply_text(
#             "⚠️ Could not fetch enough data for one or both tickers.\n"
#             "Please check the ticker symbols are valid.",
#             parse_mode="Markdown"
#         )
#         return

#     chart_path = generate_comparison_chart(
#         ticker1, history1,
#         ticker2, history2
#     )

#     if not chart_path:
#         await update.message.reply_text("❌ Failed to generate comparison chart.")
#         return

#     try:
#         with open(chart_path, "rb") as photo:
#             await update.message.reply_photo(
#                 photo=photo,
#                 caption=(
#                     f"📊 *{ticker1} vs {ticker2}*\n"
#                     f"Last 7 days — prices in ₹"
#                 ),
#                 parse_mode="Markdown"
#             )
#     finally:
#         if os.path.exists(chart_path):
#             os.remove(chart_path)

# # ─── /news ────────────────────────────────────────────────────
# async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Fetch latest Indian market news on demand.
#     Usage:
#       /news           → top 10 general market news
#       /news TICKER    → news for a specific stock
#     """
#     _track(update)

#     from api.news_api import get_market_news, get_stock_news

#     # Per stock news
#     if context.args:
#         ticker = context.args[0].upper().strip()
#         await update.message.reply_text(
#             f"🔍 Fetching news for `{ticker}`...",
#             parse_mode="Markdown"
#         )

#         articles = get_stock_news(ticker, max_articles=5)

#         if not articles:
#             await update.message.reply_text(
#                 f"❌ No news found for `{ticker}` right now.",
#                 parse_mode="Markdown"
#             )
#             return

#         lines = [f"📌 *Latest News — {ticker}*\n"]
#         for a in articles:
#             lines.append(
#                 f"• [{a['title']}]({a['url']})\n"
#                 f"  _— {a['source']} · {a['published_at']}_"
#             )

#         await update.message.reply_text(
#             "\n\n".join(lines),
#             parse_mode="Markdown",
#             disable_web_page_preview=True
#         )

#     # General market news
#     else:
#         await update.message.reply_text("🔍 Fetching latest market news...")

#         articles = get_market_news(max_articles=10)

#         if not articles:
#             await update.message.reply_text(
#                 "❌ No news available right now. Try again later."
#             )
#             return

#         lines = ["📰 *Top Indian Market News*\n"]
#         for i, a in enumerate(articles, 1):
#             lines.append(
#                 f"{i}. [{a['title']}]({a['url']})\n"
#                 f"   _— {a['source']} · {a['published_at']}_"
#             )

#         await update.message.reply_text(
#             "\n\n".join(lines),
#             parse_mode="Markdown",
#             disable_web_page_preview=True
#         )


# bot/handlers.py
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler, filters
import yfinance as yf

from data.database import (
    add_symbol, remove_symbol, get_watchlist,
    get_price_history, set_alert,
    get_all_alert_settings
)
from api.market_api import get_price

logger = logging.getLogger(__name__)

# ─── Analytics Helper ─────────────────────────────────────────
def _track(update: Update):
    """
    Call at the start of every command handler.
    Silently logs the user — never blocks the command.
    """
    try:
        from data.database import track_user
        user = update.effective_user
        track_user(
            chat_id    = str(update.effective_chat.id),
            username   = user.username   or "",
            first_name = user.first_name or ""
        )
    except Exception:
        pass  # analytics should never crash the bot


# ─── /stats ───────────────────────────────────────────────────
# async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Show bot usage analytics. Only works for the bot owner."""
#     _track(update)

#     # Only you can see stats
#     owner_chat_id = os.getenv("TELEGRAM_CHAT_ID")
#     if str(update.effective_chat.id) != str(owner_chat_id):
#         await update.message.reply_text(
#             "⚠️ This command is only available to the bot owner."
#         )
#         return

#     try:
#         from data.database import supabase
#         result = supabase.table("bot_users").select("*").execute()
#         users  = result.data

#         if not users:
#             await update.message.reply_text("No users yet.")
#             return

#         total_users    = len(users)
#         total_commands = sum(u["command_count"] for u in users)

#         # Most active users
#         top_users = sorted(users, key=lambda u: u["command_count"], reverse=True)[:5]
#         top_lines = "\n".join([
#             f"  {i+1}. {u['first_name']} (@{u['username']}) "
#             f"— {u['command_count']} commands"
#             for i, u in enumerate(top_users)
#         ])

#         await update.message.reply_text(
#             f"📊 *Bot Analytics*\n\n"
#             f"👥 Total users:    *{total_users}*\n"
#             f"⚡ Total commands: *{total_commands}*\n\n"
#             f"🏆 *Most Active Users:*\n{top_lines}",
#             parse_mode="Markdown"
#         )

#     except Exception as e:
#         await update.message.reply_text(f"❌ Failed to fetch stats: {e}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _track(update)

    owner_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if str(update.effective_chat.id) != str(owner_chat_id):
        await update.message.reply_text(
            "⚠️ This command is only available to the bot owner."
        )
        return

    try:
        from data.database import supabase
        result = supabase.table("bot_users").select("*").execute()
        users  = result.data

        if not users:
            await update.message.reply_text("No users yet.")
            return

        total_users    = len(users)
        total_commands = sum(u["command_count"] for u in users)

        top_users = sorted(
            users,
            key=lambda u: u["command_count"],
            reverse=True
        )[:5]

        # ← Fix: don't use Markdown for usernames
        # plain text avoids all parse errors
        top_lines = "\n".join([
            f"  {i+1}. {u['first_name']} "
            f"({u['command_count']} commands)"
            for i, u in enumerate(top_users)
        ])

        # Send as plain text — no parse_mode
        await update.message.reply_text(
            f"📊 Bot Analytics\n\n"
            f"👥 Total users:    {total_users}\n"
            f"⚡ Total commands: {total_commands}\n\n"
            f"🏆 Most Active Users:\n{top_lines}"
            # ← no parse_mode here
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to fetch stats: {e}")



# ─── General Message Handler ──────────────────────────────────
async def general_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _track(update)
    """Responds to casual messages like 'hi', 'hello' etc."""
    text = update.message.text.lower().strip()

    greetings = {"hi", "hello", "hey", "hii", "helo", "namaste"}

    if any(word in text for word in greetings):
        await update.message.reply_text(
            "👋 Hey! I'm *Market Price Tracker Bot*\n\n"
            "I help you track Indian stocks and gold prices in real time.\n\n"
            "📈 *What I can do:*\n"
            "• Track NSE/BSE stocks in ₹\n"
            "• Track Gold prices per 10g in ₹\n"
            "• Alert you on price drops or rises\n"
            "• Send daily market summary at 3:45 PM\n"
            "• Show 7-day price charts\n\n"
            "⚡ *Commands:*\n"
            "/add `TICKER` — Add stock to watchlist\n"
            "/remove `TICKER` — Remove stock\n"
            "/watchlist — View all tracked stocks\n"
            "/price `TICKER` — Get current price\n"
            "/alert `TICKER` drop/rise/both `%` — Set alert\n"
            "/graph `TICKER` — View 7-day chart\n"
            "/compare `TICKER1` `TICKER2` — Compare two stocks\n"
            "/news — Get latest market news\n"
            "/stats — Show bot usage analytics\n\n"
            "💡 *Examples:*\n"
            "`/add RELIANCE.NS`\n"
            "`/add GOLD`\n"
            "`/alert TCS.NS drop 2.0`"
            "`/compare RELIANCE.NS TCS.NS`\n",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "🤖 I only understand commands. Type `/start` to see what I can do!",
            parse_mode="Markdown"
        )


# ─── /start ───────────────────────────────────────────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message shown when user first opens the bot."""
    _track(update)
    await update.message.reply_text(
        "👋 Welcome to *Market Tracker Bot!*\n\n"
        "Here's what I can do:\n\n"
        "📈 `/add TICKER` — Add a stock to your watchlist\n"
        "🗑 `/remove TICKER` — Remove a stock\n"
        "📋 `/watchlist` — View all tracked stocks\n"
        "💰 `/price TICKER` — Get current price\n"
        "🔔 `/alert TICKER 2.5` — Alert if price drops 2.5%\n"
        "📊 `/news` — Get latest market news\n"
        "📊 `/graph TICKER` — View 7-day price chart\n"
        "🔴compare `TICKER1` `TICKER2` — Compare two stocks\n\n"
        "_Examples:_\n"
        "`/add RELIANCE.NS`\n"
        "`/add TCS.NS`\n"
        "`/add GOLD`\n"
        "`/price INFY.NS`\n"
        "`/compare RELIANCE.NS TCS.NS`\n"
        "`/alert RELIANCE.NS 2.0`",
        parse_mode="Markdown"
    )


# ─── /add ─────────────────────────────────────────────────────
# async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     _track(update)
#     chat_id = str(update.effective_chat.id)
#     if not context.args:
#         await update.message.reply_text(
#             "⚠️ Please provide a ticker.\n"
#             "Example: `/add RELIANCE.NS`",
#             parse_mode="Markdown"
#         )
#         return

#     ticker = context.args[0].upper().strip()

#     # Special handling — if user types just GOLD, guide them
#     if ticker == "GOLD":
#         await update.message.reply_text(
#             "🥇 *Which gold karat would you like to track?*\n\n"
#             "`/add GOLD_24K` — 24K (pure gold, investment)\n"
#             "`/add GOLD_22K` — 22K (jewellery standard)\n"
#             "`/add GOLD_18K` — 18K (studded jewellery)\n\n"
#             "_You can add multiple karats to your watchlist!_",
#             parse_mode="Markdown"
#         )
#         return

#     await update.message.reply_text(
#         f"🔍 Checking `{ticker}`...", parse_mode="Markdown"
#     )

#     GOLD_TICKERS = {"GC=F", "GOLD_24K", "GOLD_22K", "GOLD_18K", "XAU"}
#     if ticker not in GOLD_TICKERS:
#         data = yf.Ticker(ticker).history(period="1d")
#         if data.empty:
#             await update.message.reply_text(
#                 f"❌ `{ticker}` doesn't exist or has no data.\n\n"
#                 f"💡 Tips:\n"
#                 f"• NSE stocks: add `.NS` → `RELIANCE.NS`\n"
#                 f"• BSE stocks: add `.BO` → `RELIANCE.BO`\n"
#                 f"• Gold: use `GOLD_24K`, `GOLD_22K`, or `GOLD_18K`",
#                 parse_mode="Markdown"
#             )
#             return

#     success = add_symbol(ticker, chat_id)
#     if not success:
#         await update.message.reply_text(
#             f"⚠️ `{ticker}` is already in your watchlist.",
#             parse_mode="Markdown"
#         )
#         return

#     result = get_price(ticker)
#     if result:
#         await update.message.reply_text(
#             f"✅ `{ticker}` added to your watchlist!\n\n"
#             f"💰 Current price: *₹{result['price']}* {result['unit']}\n"
#             f"🏦 Exchange: {result['exchange']}",
#             parse_mode="Markdown"
#         )
#     else:
#         await update.message.reply_text(
#             f"✅ `{ticker}` added!\n"
#             f"_(Price will be fetched on next scheduler run)_",
#             parse_mode="Markdown"
#         )

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _track(update)
    chat_id = str(update.effective_chat.id)

    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a stock name or ticker.\n"
            "Examples:\n"
            "`/add reliance`\n"
            "`/add RELIANCE.NS`\n"
            "`/add GOLD_24K`",
            parse_mode="Markdown"
        )
        return

    query  = context.args[0].strip()
    ticker = query.upper()

    # ── Gold shortcut ──
    if ticker == "GOLD":
        await update.message.reply_text(
            "🥇 *Which gold karat would you like to track?*\n\n"
            "`/add GOLD_24K` — 24K (pure gold, investment)\n"
            "`/add GOLD_22K` — 22K (jewellery standard)\n"
            "`/add GOLD_18K` — 18K (studded jewellery)\n\n"
            "_You can add multiple karats!_",
            parse_mode="Markdown"
        )
        return

    GOLD_TICKERS = {"GC=F", "GOLD_24K", "GOLD_22K", "GOLD_18K", "XAU"}

    # ── If exact ticker format provided (has . or _) → add directly ──
    if "." in ticker or "_" in ticker or ticker in GOLD_TICKERS:
        await _add_ticker_directly(update, ticker, chat_id)
        return

    # ── Fuzzy search — user typed a name like "reliance" ──
    await _fuzzy_search(update, query, action="addticker")


async def _add_ticker_directly(update, ticker, chat_id):
    """Add a ticker directly without fuzzy search.
    Works when called from both command handlers and button callbacks.
    """
    GOLD_TICKERS = {"GC=F", "GOLD_24K", "GOLD_22K", "GOLD_18K", "XAU"}

    # Support being called from either a command or a callback query
    if update.callback_query:
        reply = update.callback_query.message.reply_text
    else:
        reply = update.message.reply_text

    await reply(
        f"🔍 Checking `{ticker}`...",
        parse_mode="Markdown"
    )

    if ticker not in GOLD_TICKERS:
        import yfinance as yf
        data = yf.Ticker(ticker).history(period="1d")
        if data.empty:
            await reply(
                f"❌ `{ticker}` doesn't exist or has no data.\n\n"
                f"💡 Tips:\n"
                f"• NSE stocks: add `.NS` → `RELIANCE.NS`\n"
                f"• BSE stocks: add `.BO` → `RELIANCE.BO`\n"
                f"• Gold: use `GOLD_24K`, `GOLD_22K`, or `GOLD_18K`",
                parse_mode="Markdown"
            )
            return

    success = add_symbol(ticker, chat_id)
    if not success:
        await reply(
            f"⚠️ `{ticker}` is already in your watchlist.",
            parse_mode="Markdown"
        )
        return

    from api.market_api import get_price
    result = get_price(ticker)
    if result:
        await reply(
            f"✅ `{ticker}` added to your watchlist!\n\n"
            f"💰 Current price: *₹{result['price']}* {result['unit']}\n"
            f"🏦 Exchange: {result['exchange']}",
            parse_mode="Markdown"
        )
    else:
        await reply(
            f"✅ `{ticker}` added!\n"
            f"_(Price fetched on next scheduler run)_",
            parse_mode="Markdown"
        )


async def _fuzzy_search(update, query: str, action: str):
    """
    Search yfinance for `query` and show inline buttons with callback_data = f"{action}:{symbol}".
    Reused by /price, /remove, /graph, /alert, /add.
    """
    await update.message.reply_text(
        f"🔍 Searching for *{query}*...",
        parse_mode="Markdown"
    )

    try:
        search_results = yf.Search(query, max_results=6).quotes
    except Exception as e:
        logger.error(f"yfinance search failed: {e}")
        search_results = []

    if not search_results:
        await update.message.reply_text(
            f"❌ No results found for *{query}*.\n\n"
            f"Try using the exact ticker:\n"
            f"`RELIANCE.NS` for NSE\n"
            f"`RELIANCE.BO` for BSE",
            parse_mode="Markdown"
        )
        return

    indian = [
        r for r in search_results
        if r.get("symbol", "").endswith((".NS", ".BO"))
    ][:6]
    if not indian:
        indian = search_results[:6]

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    buttons = []
    for r in indian:
        symbol   = r.get("symbol", "")
        exchange = "NSE" if symbol.endswith(".NS") else \
                   "BSE" if symbol.endswith(".BO") else "INT"
        buttons.append([
            InlineKeyboardButton(
                f"{symbol} — {exchange}",
                callback_data=f"{action}:{symbol}"
            )
        ])

    await update.message.reply_text(
        f"🔍 *Results for '{query}':*\n\nTap to select:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )



# ─── /remove ──────────────────────────────────────────────────
async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Remove a stock from the watchlist.
    Usage: /remove RELIANCE.NS  or  /remove reliance  (fuzzy search)
    """
    _track(update)
    chat_id = str(update.effective_chat.id)
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a ticker or name.\n"
            "Example: `/remove RELIANCE.NS` or `/remove reliance`",
            parse_mode="Markdown"
        )
        return

    query  = context.args[0].strip()
    ticker = query.upper()

    # Fuzzy search if name given (no . or _)
    if "." not in ticker and "_" not in ticker:
        await _fuzzy_search(update, query, action="remove")
        return

    # Check it's actually in the user's watchlist first
    watchlist = get_watchlist(chat_id)
    if ticker not in watchlist:
        await update.message.reply_text(
            f"⚠️ `{ticker}` is not in your watchlist.",
            parse_mode="Markdown"
        )
        return

    remove_symbol(ticker, chat_id)
    await update.message.reply_text(
        f"🗑 `{ticker}` removed from your watchlist.",
        parse_mode="Markdown"
    )

# ─── /watchlist Phase 1 code ───────────────────────────────────────────────
# async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Show all tracked stocks with their latest prices."""
#     watchlist = get_watchlist()

#     if not watchlist:
#         await update.message.reply_text(
#             "📋 Your watchlist is empty.\n\n"
#             "Add stocks with `/add RELIANCE.NS`",
#             parse_mode="Markdown"
#         )
#         return

#     await update.message.reply_text("⏳ Fetching latest prices...")

#     lines = ["📋 *Your Watchlist*\n"]
#     for ticker in watchlist:
#         result = get_price(ticker)
#         if result:
#             lines.append(
#                 f"• `{ticker}` — *₹{result['price']}* {result['unit']}"
#             )
#         else:
#             lines.append(f"• `{ticker}` — _price unavailable_")

#     await update.message.reply_text(
#         "\n".join(lines),
#         parse_mode="Markdown"
#     )

# ─── /watchlist Phase 2 Improved ───────────────────────────────────────────────
async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show all tracked stocks with live prices and inline action buttons.
    Each stock gets its own message with [Graph] [Alert] [Remove] buttons.
    """
    _track(update)
    chat_id = str(update.effective_chat.id)
    watchlist = get_watchlist(chat_id)

    if not watchlist:
        await update.message.reply_text(
            "📋 Your watchlist is empty.\n\n"
            "Add stocks with `/add RELIANCE.NS`",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text("⏳ Fetching latest prices...")

    from bot.keyboards import watchlist_keyboard

    for ticker in watchlist:
        result = get_price(ticker)

        if result:
            price_line = f"💰 *₹{result['price']}* {result['unit']}"
            exchange   = f"🏦 {result['exchange']}"
        else:
            price_line = "💰 _price unavailable_"
            exchange   = ""

        # Each stock is its own message with buttons below it
        await update.message.reply_text(
            f"📌 *{ticker}*\n{price_line}\n{exchange}",
            parse_mode="Markdown",
            reply_markup=watchlist_keyboard(ticker)
        )

# ─── Inline Button Callbacks ───────────────────────────────────
# async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Handles all inline button taps from the watchlist.
#     Parses callback_data in format "action:TICKER"
#     """
#     query  = update.callback_query
#     await query.answer()  # ← removes the loading spinner on the button

#     # Parse the callback data
#     parts  = query.data.split(":", 1)
#     if len(parts) != 2:
#         return

#     action, ticker = parts[0], parts[1]

#     # ── Graph button ──────────────────────────────────────────
#     if action == "graph":
#         await query.message.reply_text(
#             f"📊 Generating chart for `{ticker}`...",
#             parse_mode="Markdown"
#         )

#         from data.database import get_price_history
#         from core.graph import generate_price_chart
#         import os

#         history = get_price_history(ticker, days=7)

#         if not history or len(history) < 2:
#             await query.message.reply_text(
#                 f"⚠️ Not enough price history for `{ticker}` yet.\n"
#                 f"Check back tomorrow!",
#                 parse_mode="Markdown"
#             )
#             return

#         chart_path = generate_price_chart(ticker, history)
#         if not chart_path:
#             await query.message.reply_text(
#                 f"❌ Failed to generate chart for `{ticker}`."
#             )
#             return

#         try:
#             with open(chart_path, "rb") as photo:
#                 await query.message.reply_photo(
#                     photo=photo,
#                     caption=(
#                         f"📊 *{ticker}* — Last {len(history)} days\n"
#                         f"Latest: *₹{history[0]['closing_price']}*"
#                     ),
#                     parse_mode="Markdown"
#                 )
#         finally:
#             if os.path.exists(chart_path):
#                 os.remove(chart_path)

#     # ── Remove button ─────────────────────────────────────────
#     elif action == "remove":
#         from data.database import remove_symbol
#         chat_id = str(query.message.chat.id)
#         remove_symbol(ticker, chat_id)

#         # Edit the original message to show it's been removed
#         # instead of sending a new message
#         await query.edit_message_text(
#             f"🗑 *{ticker}* removed from your watchlist.",
#             parse_mode="Markdown"
#         )

#     # ── Alert button ──────────────────────────────────────────
#     elif action == "alert":
#         await query.message.reply_text(
#             f"🔔 *Set Alert for {ticker}*\n\n"
#             f"Use the command:\n"
#             f"`/alert {ticker} drop 2.0` — notify if drops 2%\n"
#             f"`/alert {ticker} rise 3.0` — notify if rises 3%\n"
#             f"`/alert {ticker} both 2.0` — notify either way\n\n"
#             f"_Replace `2.0` with your desired percentage._",
#             parse_mode="Markdown"
#         )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":", 1)
    if len(parts) != 2:
        return

    action, ticker = parts[0], parts[1]
    chat_id = str(update.effective_chat.id)

    # ── Add ticker from fuzzy search result ──
    if action == "addticker":
        await _add_ticker_directly(update, ticker, chat_id)
        return

    # ── Price button (from fuzzy search) ──
    if action == "price":
        result = get_price(ticker)
        if not result:
            await query.message.reply_text(
                f"❌ Could not fetch price for `{ticker}`.",
                parse_mode="Markdown"
            )
            return
        await query.message.reply_text(
            f"💰 *{ticker}*\n\n"
            f"Price:    *₹{result['price']}* {result['unit']}\n"
            f"Exchange: {result['exchange']}",
            parse_mode="Markdown"
        )
        return

    # ── Graph button ──
    if action == "graph":
        await query.message.reply_text(
            f"📊 Generating chart for `{ticker}`...",
            parse_mode="Markdown"
        )
        from data.database import get_price_history
        from core.graph import generate_price_chart
        import os

        history = get_price_history(ticker, days=7)
        if not history or len(history) < 2:
            await query.message.reply_text(
                f"⚠️ Not enough price history for `{ticker}` yet.",
                parse_mode="Markdown"
            )
            return

        chart_path = generate_price_chart(ticker, history)
        if not chart_path:
            await query.message.reply_text(f"❌ Failed to generate chart.")
            return

        try:
            with open(chart_path, "rb") as photo:
                await query.message.reply_photo(
                    photo=photo,
                    caption=(
                        f"📊 *{ticker}* — Last {len(history)} days\n"
                        f"Latest: *₹{history[0]['closing_price']}*"
                    ),
                    parse_mode="Markdown"
                )
        finally:
            if os.path.exists(chart_path):
                os.remove(chart_path)

    # ── Remove button ──
    elif action == "remove":
        watchlist = get_watchlist(chat_id)
        if ticker not in watchlist:
            await query.answer(
                f"{ticker} is not in your watchlist.", show_alert=True
            )
            return
        remove_symbol(ticker, chat_id)
        await query.edit_message_text(
            f"🗑 {ticker} removed from your watchlist."
        )

    # ── Alert button ──
    elif action == "alert":
        await query.message.reply_text(
            f"🔔 Set Alert for {ticker}\n\n"
            f"Use the command:\n"
            f"/alert {ticker} drop 2.0\n"
            f"/alert {ticker} rise 3.0\n"
            f"/alert {ticker} both 2.0"
        )



# ─── /price ───────────────────────────────────────────────────
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Get the current price of any stock instantly.
    Usage: /price TCS.NS  or  /price tata  (fuzzy search)
    """
    _track(update)
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a ticker or name.\n"
            "Example: `/price TCS.NS` or `/price tata`",
            parse_mode="Markdown"
        )
        return

    query  = context.args[0].strip()
    ticker = query.upper()

    # Fuzzy search if name given (no . or _)
    if "." not in ticker and "_" not in ticker:
        await _fuzzy_search(update, query, action="price")
        return

    result = get_price(ticker)

    if not result:
        await update.message.reply_text(
            f"❌ Could not fetch price for `{ticker}`.\n"
            f"Make sure the ticker is valid.",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"💰 *{ticker}*\n\n"
        f"Price:    *₹{result['price']}* {result['unit']}\n"
        f"Exchange: {result['exchange']}",
        parse_mode="Markdown"
    )


# ─── /alert ───────────────────────────────────────────────────
async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set a price alert for a stock.
    Usage:
      /alert RELIANCE.NS drop 2.0
      /alert RELIANCE.NS rise 3.0
      /alert RELIANCE.NS both 2.0
      /alert reliance          → fuzzy search, then shows alert instructions
    """
    _track(update)
    chat_id = str(update.effective_chat.id)

    # Fuzzy search if only 1 arg given and it looks like a name (no . or _)
    if len(context.args) == 1:
        arg = context.args[0].strip()
        if "." not in arg.upper() and "_" not in arg.upper():
            await _fuzzy_search(update, arg, action="alert")
            return

    if len(context.args) < 3:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "`/alert TICKER drop 2.0`\n"
            "`/alert TICKER rise 3.0`\n"
            "`/alert TICKER both 2.0`\n\n"
            "_Examples:_\n"
            "`/alert RELIANCE.NS drop 2.0` — notify if drops 2%\n"
            "`/alert TCS.NS rise 3.0` — notify if rises 3%\n"
            "`/alert GOLD both 1.5` — notify if moves 1.5% either way",
            parse_mode="Markdown"
        )
        return

    ticker    = context.args[0].upper().strip()
    direction = context.args[1].lower().strip()

    # Validate direction
    if direction not in ("drop", "rise", "both"):
        await update.message.reply_text(
            "⚠️ Direction must be `drop`, `rise`, or `both`.\n"
            "Example: `/alert RELIANCE.NS drop 2.0`",
            parse_mode="Markdown"
        )
        return

    # Validate threshold
    try:
        threshold = float(context.args[2])
        if threshold <= 0 or threshold > 100:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "⚠️ Please provide a valid percentage between 0 and 100.\n"
            "Example: `/alert RELIANCE.NS drop 2.5`",
            parse_mode="Markdown"
        )
        return

    # Check ticker is in watchlist
    watchlist = get_watchlist(chat_id)
    if ticker not in watchlist:
        await update.message.reply_text(
            f"⚠️ `{ticker}` is not in your watchlist.\n"
            f"Add it first with `/add {ticker}`",
            parse_mode="Markdown"
        )
        return

    set_alert(ticker, direction, threshold)

    # Build a clear confirmation message
    if direction == "drop":
        detail = f"📉 Notify if drops more than *{threshold}%*"
    elif direction == "rise":
        detail = f"📈 Notify if rises more than *{threshold}%*"
    else:
        detail = f"📉📈 Notify if moves more than *{threshold}%* either way"

    await update.message.reply_text(
        f"🔔 Alert set for `{ticker}`!\n\n{detail}",
        parse_mode="Markdown"
    )



# ─── /graph ───────────────────────────────────────────────────
async def graph_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /graph RELIANCE.NS       → single stock chart
    /graph GOLD_24K          → single karat chart
    /graph GOLD compare      → 24K vs 22K comparison chart
    /graph reliance          → fuzzy search, then chart
    """
    _track(update)
    chat_id = str(update.effective_chat.id)
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a ticker or name.\n"
            "Examples:\n"
            "`/graph RELIANCE.NS`\n"
            "`/graph GOLD_24K`\n"
            "`/graph reliance`",
            parse_mode="Markdown"
        )
        return

    from data.database import get_price_history
    from core.graph import generate_price_chart, generate_gold_comparison_chart
    import os

    query  = context.args[0].strip()
    ticker = query.upper()

    # Fuzzy search if name given (no . or _), but not the special GOLD keyword
    if "." not in ticker and "_" not in ticker and ticker != "GOLD":
        await _fuzzy_search(update, query, action="graph")
        return

    # ── Special case: /graph GOLD compare ──
    if ticker == "GOLD" and len(context.args) > 1 and context.args[1].lower() == "compare":
        await update.message.reply_text("📊 Generating gold comparison chart...")

        histories = {
            "GOLD_24K": get_price_history("GOLD_24K", days=7),
            "GOLD_22K": get_price_history("GOLD_22K", days=7),
        }

        if all(len(h) < 2 for h in histories.values()):
            await update.message.reply_text(
                "⚠️ Not enough price history yet.\n"
                "Add `GOLD_24K` and `GOLD_22K` to your watchlist first.",
                parse_mode="Markdown"
            )
            return

        chart_path = generate_gold_comparison_chart(histories)
        if not chart_path:
            await update.message.reply_text("❌ Failed to generate comparison chart.")
            return

        try:
            with open(chart_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption="📊 *Gold Comparison — 24K vs 22K*\nper 10g in ₹",
                    parse_mode="Markdown"
                )
        finally:
            if os.path.exists(chart_path):
                os.remove(chart_path)
        return

    # ── Single ticker chart ──
    watchlist = get_watchlist(chat_id)
    if ticker not in watchlist:
        await update.message.reply_text(
            f"⚠️ `{ticker}` is not in your watchlist.\n"
            f"Add it first with `/add {ticker}`",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"📊 Generating chart for `{ticker}`...",
        parse_mode="Markdown"
    )

    history = get_price_history(ticker, days=7)

    if not history or len(history) < 2:
        await update.message.reply_text(
            f"⚠️ Not enough price history for `{ticker}` yet.\n"
            f"Check back tomorrow!",
            parse_mode="Markdown"
        )
        return

    chart_path = generate_price_chart(ticker, history)
    if not chart_path:
        await update.message.reply_text(
            f"❌ Failed to generate chart for `{ticker}`.",
            parse_mode="Markdown"
        )
        return

    try:
        with open(chart_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=(
                    f"📊 *{ticker}* — Last {len(history)} days\n"
                    f"Latest: *₹{history[0]['closing_price']}*"
                ),
                parse_mode="Markdown"
            )
    finally:
        if os.path.exists(chart_path):
            os.remove(chart_path)
            logger.info(f"Temp chart deleted: {chart_path}")


# ─── /compare ─────────────────────────────────────────────────
async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Compare two tickers on the same chart.
    Usage:
      /compare RELIANCE.NS TCS.NS
      /compare GOLD_24K GOLD_22K
    """
    _track(update)
    chat_id = str(update.effective_chat.id)
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Please provide two tickers.\n\n"
            "Examples:\n"
            "`/compare RELIANCE.NS TCS.NS`\n"
            "`/compare GOLD_24K GOLD_22K`",
            parse_mode="Markdown"
        )
        return

    ticker1 = context.args[0].upper().strip()
    ticker2 = context.args[1].upper().strip()

    if ticker1 == ticker2:
        await update.message.reply_text(
            "⚠️ Please provide two *different* tickers.",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"📊 Comparing `{ticker1}` vs `{ticker2}`...",
        parse_mode="Markdown"
    )

    from data.database import get_price_history
    from api.market_api import get_price_history_api
    from core.graph import generate_comparison_chart
    import os

    # Try DB first, fall back to live API fetch if not enough data
    history1 = get_price_history(ticker1, days=7)
    history2 = get_price_history(ticker2, days=7)

    if len(history1) < 2:
        await update.message.reply_text(
            f"⏳ Fetching history for `{ticker1}`...",
            parse_mode="Markdown"
        )
        history1 = get_price_history_api(ticker1, days=7)
        # Save to DB for future use
        from data.database import upsert_price
        for entry in history1:
            upsert_price(ticker1, entry["date"], entry["closing_price"])

    if len(history2) < 2:
        await update.message.reply_text(
            f"⏳ Fetching history for `{ticker2}`...",
            parse_mode="Markdown"
        )
        history2 = get_price_history_api(ticker2, days=7)
        from data.database import upsert_price
        for entry in history2:
            upsert_price(ticker2, entry["date"], entry["closing_price"])

    if len(history1) < 2 or len(history2) < 2:
        await update.message.reply_text(
            "⚠️ Could not fetch enough data for one or both tickers.\n"
            "Please check the ticker symbols are valid.",
            parse_mode="Markdown"
        )
        return

    chart_path = generate_comparison_chart(
        ticker1, history1,
        ticker2, history2
    )

    if not chart_path:
        await update.message.reply_text("❌ Failed to generate comparison chart.")
        return

    try:
        with open(chart_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=(
                    f"📊 *{ticker1} vs {ticker2}*\n"
                    f"Last 7 days — prices in ₹"
                ),
                parse_mode="Markdown"
            )
    finally:
        if os.path.exists(chart_path):
            os.remove(chart_path)

# ─── /news ────────────────────────────────────────────────────
async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fetch latest Indian market news on demand.
    Usage:
      /news           → top 10 general market news
      /news TICKER    → news for a specific stock
    """
    _track(update)

    from api.news_api import get_market_news, get_stock_news

    if context.args:
        ticker = context.args[0].upper().strip()
        await update.message.reply_text(
            f"🔍 Fetching news for `{ticker}`...",
            parse_mode="Markdown"
        )

        articles = get_stock_news(ticker, max_articles=5)

        if not articles:
            await update.message.reply_text(
                f"❌ No news found for `{ticker}` right now.",
                parse_mode="Markdown"
            )
            return

        lines = [f"📌 *Latest News — {ticker}*\n"]
        for a in articles:
            lines.append(
                f"• [{a['title']}]({a['url']})\n"
                f"  _— {a['source']} · {a['published_at']}_"
            )

        await update.message.reply_text(
            "\n\n".join(lines),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

    else:
        await update.message.reply_text("🔍 Fetching latest market news...")

        articles = get_market_news(max_articles=10)

        if not articles:
            await update.message.reply_text(
                "❌ No news available right now. Try again later."
            )
            return

        lines = ["📰 *Top Indian Market News*\n"]
        for i, a in enumerate(articles, 1):
            lines.append(
                f"{i}. [{a['title']}]({a['url']})\n"
                f"   _— {a['source']} · {a['published_at']}_"
            )

        await update.message.reply_text(
            "\n\n".join(lines),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )