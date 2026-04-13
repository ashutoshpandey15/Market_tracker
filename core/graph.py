# # core/graph.py
# import logging
# import os
# import tempfile
# from datetime import datetime

# import matplotlib
# matplotlib.use("Agg")  # ← headless mode, no display window needed
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from matplotlib.patches import FancyBboxPatch
# import numpy as np

# logger = logging.getLogger(__name__)


# def generate_price_chart(ticker: str, history: list[dict]) -> str | None:
#     """
#     Generate a 7-day price chart for a ticker.

#     Args:
#         ticker:  e.g. 'RELIANCE.NS'
#         history: list of { date, closing_price } dicts from DB

#     Returns:
#         Path to the saved .png file, or None if generation failed.
#         Caller is responsible for deleting the file after sending.
#     """
#     if not history or len(history) < 2:
#         logger.warning(f"Not enough data to plot chart for {ticker}")
#         return None

#     try:
#         # ── Prepare data ──────────────────────────────────────
#         # Sort oldest → newest
#         history = sorted(history, key=lambda x: x["date"])

#         dates  = [datetime.strptime(e["date"], "%Y-%m-%d") for e in history]
#         prices = [float(e["closing_price"]) for e in history]

#         first_price = prices[0]
#         last_price  = prices[-1]
#         change_pct  = ((last_price - first_price) / first_price) * 100
#         is_positive = change_pct >= 0

#         # Color scheme based on direction
#         line_color = "#00C853" if is_positive else "#FF3D00"  # green or red
#         fill_color = "#00C853" if is_positive else "#FF3D00"
#         arrow      = "▲" if is_positive else "▼"
#         sign       = "+" if is_positive else ""

#         # ── Figure setup ──────────────────────────────────────
#         fig, ax = plt.subplots(figsize=(10, 5))
#         fig.patch.set_facecolor("#1E1E2E")   # dark background
#         ax.set_facecolor("#1E1E2E")

#         # ── Plot line ─────────────────────────────────────────
#         ax.plot(
#             dates, prices,
#             color=line_color,
#             linewidth=2.5,
#             zorder=3
#         )

#         # ── Fill area under line ──────────────────────────────
#         ax.fill_between(
#             dates, prices, min(prices),
#             alpha=0.15,
#             color=fill_color,
#             zorder=2
#         )

#         # ── Dot on last price ─────────────────────────────────
#         ax.scatter(
#             [dates[-1]], [last_price],
#             color=line_color,
#             s=80,
#             zorder=5
#         )

#         # ── Price label on last point ─────────────────────────
#         ax.annotate(
#             f"₹{last_price:,.2f}",
#             xy=(dates[-1], last_price),
#             xytext=(10, 5),
#             textcoords="offset points",
#             color="white",
#             fontsize=10,
#             fontweight="bold"
#         )

#         # ── Axes formatting ───────────────────────────────────
#         ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
#         ax.xaxis.set_major_locator(mdates.DayLocator())
#         plt.xticks(rotation=45, color="#AAAAAA", fontsize=9)
#         plt.yticks(color="#AAAAAA", fontsize=9)

#         # Format Y axis with ₹ symbol
#         ax.yaxis.set_major_formatter(
#             plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}")
#         )

#         # ── Grid ──────────────────────────────────────────────
#         ax.grid(
#             True,
#             color="#333355",
#             linestyle="--",
#             linewidth=0.5,
#             alpha=0.7
#         )
#         ax.set_axisbelow(True)

#         # ── Spines ────────────────────────────────────────────
#         for spine in ax.spines.values():
#             spine.set_color("#333355")

#         # ── Title ─────────────────────────────────────────────
#         display_name = ticker.replace(".NS", " (NSE)").replace(".BO", " (BSE)")
#         if ticker == "GOLD":
#             display_name = "Gold (per 10g)"

#         fig.suptitle(
#             f"{display_name}   {arrow} {sign}{change_pct:.2f}%  "
#             f"over {len(prices)} days",
#             color="white",
#             fontsize=13,
#             fontweight="bold",
#             y=0.98
#         )

#         # ── Subtitle: price range ─────────────────────────────
#         ax.set_title(
#             f"₹{min(prices):,.2f}  –  ₹{max(prices):,.2f}",
#             color="#AAAAAA",
#             fontsize=9,
#             pad=4
#         )

#         # ── Tight layout ──────────────────────────────────────
#         plt.tight_layout()

#         # ── Save to temp file ─────────────────────────────────
#         tmp = tempfile.NamedTemporaryFile(
#             suffix=".png",
#             delete=False,
#             prefix=f"chart_{ticker}_"
#         )
#         plt.savefig(
#             tmp.name,
#             dpi=150,
#             bbox_inches="tight",
#             facecolor=fig.get_facecolor()
#         )
#         plt.close(fig)

#         logger.info(f"Chart saved: {tmp.name}")
#         return tmp.name

#     except Exception as e:
#         logger.error(f"generate_price_chart failed for {ticker}: {e}")
#         return None

# # -------------------------------------- Comparison chart for multiple gold karats and stocks --------------------------------------
# def generate_comparison_chart(
#     ticker1: str, history1: list[dict],
#     ticker2: str, history2: list[dict]
# ) -> str | None:
#     """
#     Generate a comparison chart for two tickers.
#     Auto-detects if dual Y axis is needed based on price difference.

#     Args:
#         ticker1, ticker2: ticker strings
#         history1, history2: list of { date, closing_price } dicts

#     Returns:
#         Path to saved .png or None.
#     """
#     if not history1 or not history2:
#         logger.warning("Not enough data for comparison chart")
#         return None

#     if len(history1) < 2 or len(history2) < 2:
#         logger.warning("Need at least 2 days of data for each ticker")
#         return None

#     try:
#         # ── Prepare data ──────────────────────────────────────
#         history1 = sorted(history1, key=lambda x: x["date"])
#         history2 = sorted(history2, key=lambda x: x["date"])

#         dates1  = [datetime.strptime(e["date"], "%Y-%m-%d") for e in history1]
#         prices1 = [float(e["closing_price"]) for e in history1]

#         dates2  = [datetime.strptime(e["date"], "%Y-%m-%d") for e in history2]
#         prices2 = [float(e["closing_price"]) for e in history2]

#         # ── Auto detect if dual Y axis needed ─────────────────
#         avg1 = sum(prices1) / len(prices1)
#         avg2 = sum(prices2) / len(prices2)
#         price_ratio = max(avg1, avg2) / min(avg1, avg2)
#         use_dual_axis = price_ratio > 1.5  # if prices differ by 50%+

#         # ── Colors ────────────────────────────────────────────
#         # Gold karats get gold colors, stocks get blue/purple
#         GOLD_TICKERS = {"GOLD_24K", "GOLD_22K", "GOLD_18K", "GOLD"}

#         color1 = "#FFD700" if ticker1 in GOLD_TICKERS else "#4FC3F7"  # gold or blue
#         color2 = "#FFA500" if ticker2 in GOLD_TICKERS else "#CE93D8"  # gold or purple

#         # ── Display names ─────────────────────────────────────
#         def display_name(ticker):
#             if ticker == "GOLD_24K": return "Gold 24K"
#             if ticker == "GOLD_22K": return "Gold 22K"
#             if ticker == "GOLD_18K": return "Gold 18K"
#             return ticker.replace(".NS", " (NSE)").replace(".BO", " (BSE)")

#         label1 = display_name(ticker1)
#         label2 = display_name(ticker2)

#         # ── Figure setup ──────────────────────────────────────
#         fig, ax1 = plt.subplots(figsize=(10, 5))
#         fig.patch.set_facecolor("#1E1E2E")
#         ax1.set_facecolor("#1E1E2E")

#         # ── Plot ticker 1 on left axis ────────────────────────
#         ax1.plot(
#             dates1, prices1,
#             color=color1,
#             linewidth=2.5,
#             label=label1,
#             zorder=3
#         )
#         ax1.fill_between(dates1, prices1, min(prices1),
#                          alpha=0.1, color=color1, zorder=2)
#         ax1.scatter([dates1[-1]], [prices1[-1]],
#                     color=color1, s=60, zorder=5)
#         ax1.annotate(
#             f"₹{prices1[-1]:,.0f}",
#             xy=(dates1[-1], prices1[-1]),
#             xytext=(-60, 8),
#             textcoords="offset points",
#             color=color1,
#             fontsize=9,
#             fontweight="bold"
#         )
#         ax1.tick_params(axis="y", labelcolor=color1, labelsize=9)
#         ax1.yaxis.set_major_formatter(
#             plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}")
#         )

#         # ── Plot ticker 2 ─────────────────────────────────────
#         if use_dual_axis:
#             # Different price ranges → second Y axis on right
#             ax2 = ax1.twinx()
#             ax2.set_facecolor("#1E1E2E")
#             ax2.tick_params(axis="y", labelcolor=color2, labelsize=9)
#             ax2.yaxis.set_major_formatter(
#                 plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}")
#             )
#             ax2.spines["right"].set_color(color2)
#             ax2.spines["left"].set_color(color1)
#         else:
#             ax2 = ax1  # same axis

#         ax2.plot(
#             dates2, prices2,
#             color=color2,
#             linewidth=2.5,
#             label=label2,
#             zorder=3,
#             linestyle="--"   # dashed so lines are visually distinct
#         )
#         ax2.fill_between(dates2, prices2, min(prices2),
#                          alpha=0.08, color=color2, zorder=2)
#         ax2.scatter([dates2[-1]], [prices2[-1]],
#                     color=color2, s=60, zorder=5)
#         ax2.annotate(
#             f"₹{prices2[-1]:,.0f}",
#             xy=(dates2[-1], prices2[-1]),
#             xytext=(8, 8),
#             textcoords="offset points",
#             color=color2,
#             fontsize=9,
#             fontweight="bold"
#         )

#         # ── X axis formatting ─────────────────────────────────
#         ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
#         ax1.xaxis.set_major_locator(mdates.DayLocator())
#         plt.xticks(rotation=45, color="#AAAAAA", fontsize=9)

#         # ── Grid ──────────────────────────────────────────────
#         ax1.grid(True, color="#333355", linestyle="--",
#                  linewidth=0.5, alpha=0.7)
#         ax1.set_axisbelow(True)

#         # ── Spines ────────────────────────────────────────────
#         for spine in ax1.spines.values():
#             spine.set_color("#333355")

#         # ── Legend (combine both axes) ────────────────────────
#         lines1, labels1 = ax1.get_legend_handles_labels()
#         if use_dual_axis:
#             lines2, labels2 = ax2.get_legend_handles_labels()
#         else:
#             lines2, labels2 = [], []

#         ax1.legend(
#             lines1 + lines2,
#             labels1 + labels2,
#             facecolor="#2A2A3E",
#             edgecolor="#333355",
#             labelcolor="white",
#             fontsize=10,
#             loc="upper left"
#         )

#         # ── Title ─────────────────────────────────────────────
#         fig.suptitle(
#             f"{label1}  vs  {label2}",
#             color="white",
#             fontsize=13,
#             fontweight="bold"
#         )

#         if use_dual_axis:
#             ax1.set_title(
#                 "Dual scale — left axis vs right axis",
#                 color="#AAAAAA",
#                 fontsize=9,
#                 pad=4
#             )

#         plt.tight_layout()

#         # ── Save ──────────────────────────────────────────────
#         tmp = tempfile.NamedTemporaryFile(
#             suffix=".png",
#             delete=False,
#             prefix=f"chart_compare_"
#         )
#         plt.savefig(
#             tmp.name, dpi=150,
#             bbox_inches="tight",
#             facecolor=fig.get_facecolor()
#         )
#         plt.close(fig)

#         logger.info(f"Comparison chart saved: {tmp.name}")
#         return tmp.name

#     except Exception as e:
#         logger.error(f"generate_comparison_chart failed: {e}")
#         return None



# core/graph.py
import logging
import os
import tempfile
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # ← headless mode, no display window needed
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import numpy as np

logger = logging.getLogger(__name__)


def generate_price_chart(ticker: str, history: list[dict]) -> str | None:
    """
    Generate a 7-day price chart for a ticker.

    Args:
        ticker:  e.g. 'RELIANCE.NS'
        history: list of { date, closing_price } dicts from DB

    Returns:
        Path to the saved .png file, or None if generation failed.
        Caller is responsible for deleting the file after sending.
    """
    if not history or len(history) < 2:
        logger.warning(f"Not enough data to plot chart for {ticker}")
        return None

    try:
        # ── Prepare data ──────────────────────────────────────
        # Sort oldest → newest
        history = sorted(history, key=lambda x: x["date"])

        dates  = [datetime.strptime(e["date"], "%Y-%m-%d") for e in history]
        prices = [float(e["closing_price"]) for e in history]

        first_price = prices[0]
        last_price  = prices[-1]
        change_pct  = ((last_price - first_price) / first_price) * 100
        is_positive = change_pct >= 0

        # Color scheme based on direction
        line_color = "#00C853" if is_positive else "#FF3D00"  # green or red
        fill_color = "#00C853" if is_positive else "#FF3D00"
        arrow      = "▲" if is_positive else "▼"
        sign       = "+" if is_positive else ""

        # ── Figure setup ──────────────────────────────────────
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#1E1E2E")   # dark background
        ax.set_facecolor("#1E1E2E")

        # ── Plot line ─────────────────────────────────────────
        ax.plot(
            dates, prices,
            color=line_color,
            linewidth=2.5,
            zorder=3
        )

        # ── Fill area under line ──────────────────────────────
        ax.fill_between(
            dates, prices, min(prices),
            alpha=0.15,
            color=fill_color,
            zorder=2
        )

        # ── Dot on last price ─────────────────────────────────
        ax.scatter(
            [dates[-1]], [last_price],
            color=line_color,
            s=80,
            zorder=5
        )

        # ── Price label on last point ─────────────────────────
        ax.annotate(
            f"₹{last_price:,.2f}",
            xy=(dates[-1], last_price),
            xytext=(10, 5),
            textcoords="offset points",
            color="white",
            fontsize=10,
            fontweight="bold"
        )

        # ── Axes formatting ───────────────────────────────────
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        plt.xticks(rotation=45, color="#AAAAAA", fontsize=9)
        plt.yticks(color="#AAAAAA", fontsize=9)

        # Format Y axis with ₹ symbol
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}")
        )

        # ── Grid ──────────────────────────────────────────────
        ax.grid(
            True,
            color="#333355",
            linestyle="--",
            linewidth=0.5,
            alpha=0.7
        )
        ax.set_axisbelow(True)

        # ── Spines ────────────────────────────────────────────
        for spine in ax.spines.values():
            spine.set_color("#333355")

        # ── Title ─────────────────────────────────────────────
        display_name = ticker.replace(".NS", " (NSE)").replace(".BO", " (BSE)")
        if ticker == "GOLD":
            display_name = "Gold (per 10g)"

        fig.suptitle(
            f"{display_name}   {arrow} {sign}{change_pct:.2f}%  "
            f"over {len(prices)} days",
            color="white",
            fontsize=13,
            fontweight="bold",
            y=0.98
        )

        # ── Subtitle: price range ─────────────────────────────
        ax.set_title(
            f"₹{min(prices):,.2f}  –  ₹{max(prices):,.2f}",
            color="#AAAAAA",
            fontsize=9,
            pad=4
        )

        # ── Tight layout ──────────────────────────────────────
        plt.tight_layout()

        # ── Save to temp file ─────────────────────────────────
        tmp = tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False,
            prefix=f"chart_{ticker}_"
        )
        plt.savefig(
            tmp.name,
            dpi=150,
            bbox_inches="tight",
            facecolor=fig.get_facecolor()
        )
        plt.close(fig)

        logger.info(f"Chart saved: {tmp.name}")
        return tmp.name

    except Exception as e:
        logger.error(f"generate_price_chart failed for {ticker}: {e}")
        return None

# -------------------------------------- Comparison chart for multiple gold karats and stocks --------------------------------------
def generate_comparison_chart(
    ticker1: str, history1: list[dict],
    ticker2: str, history2: list[dict]
) -> str | None:
    """
    Generate a comparison chart for two tickers.
    Auto-detects if dual Y axis is needed based on price difference.

    Args:
        ticker1, ticker2: ticker strings
        history1, history2: list of { date, closing_price } dicts

    Returns:
        Path to saved .png or None.
    """
    if not history1 or not history2:
        logger.warning("Not enough data for comparison chart")
        return None

    if len(history1) < 2 or len(history2) < 2:
        logger.warning("Need at least 2 days of data for each ticker")
        return None

    try:
        # ── Prepare data ──────────────────────────────────────
        history1 = sorted(history1, key=lambda x: x["date"])
        history2 = sorted(history2, key=lambda x: x["date"])

        dates1  = [datetime.strptime(e["date"], "%Y-%m-%d") for e in history1]
        prices1 = [float(e["closing_price"]) for e in history1]

        dates2  = [datetime.strptime(e["date"], "%Y-%m-%d") for e in history2]
        prices2 = [float(e["closing_price"]) for e in history2]

        # ── Auto detect if dual Y axis needed ─────────────────
        avg1 = sum(prices1) / len(prices1)
        avg2 = sum(prices2) / len(prices2)
        price_ratio = max(avg1, avg2) / min(avg1, avg2)
        use_dual_axis = price_ratio > 1.5  # if prices differ by 50%+

        # ── Colors ────────────────────────────────────────────
        # Gold karats get gold colors, stocks get blue/purple
        GOLD_TICKERS = {"GOLD_24K", "GOLD_22K", "GOLD_18K", "GOLD"}

        color1 = "#FFD700" if ticker1 in GOLD_TICKERS else "#4FC3F7"  # gold or blue
        color2 = "#FFA500" if ticker2 in GOLD_TICKERS else "#CE93D8"  # gold or purple

        # ── Display names ─────────────────────────────────────
        def display_name(ticker):
            if ticker == "GOLD_24K": return "Gold 24K"
            if ticker == "GOLD_22K": return "Gold 22K"
            if ticker == "GOLD_18K": return "Gold 18K"
            return ticker.replace(".NS", " (NSE)").replace(".BO", " (BSE)")

        label1 = display_name(ticker1)
        label2 = display_name(ticker2)

        # ── Figure setup ──────────────────────────────────────
        fig, ax1 = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#1E1E2E")
        ax1.set_facecolor("#1E1E2E")

        # ── Plot ticker 1 on left axis ────────────────────────
        ax1.plot(
            dates1, prices1,
            color=color1,
            linewidth=2.5,
            label=label1,
            zorder=3
        )
        ax1.fill_between(dates1, prices1, min(prices1),
                         alpha=0.1, color=color1, zorder=2)
        ax1.scatter([dates1[-1]], [prices1[-1]],
                    color=color1, s=60, zorder=5)
        ax1.annotate(
            f"₹{prices1[-1]:,.0f}",
            xy=(dates1[-1], prices1[-1]),
            xytext=(-60, 8),
            textcoords="offset points",
            color=color1,
            fontsize=9,
            fontweight="bold"
        )
        ax1.tick_params(axis="y", labelcolor=color1, labelsize=9)
        ax1.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}")
        )

        # ── Plot ticker 2 ─────────────────────────────────────
        if use_dual_axis:
            # Different price ranges → second Y axis on right
            ax2 = ax1.twinx()
            ax2.set_facecolor("#1E1E2E")
            ax2.tick_params(axis="y", labelcolor=color2, labelsize=9)
            ax2.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}")
            )
            ax2.spines["right"].set_color(color2)
            ax2.spines["left"].set_color(color1)
        else:
            ax2 = ax1  # same axis

        ax2.plot(
            dates2, prices2,
            color=color2,
            linewidth=2.5,
            label=label2,
            zorder=3,
            linestyle="--"   # dashed so lines are visually distinct
        )
        ax2.fill_between(dates2, prices2, min(prices2),
                         alpha=0.08, color=color2, zorder=2)
        ax2.scatter([dates2[-1]], [prices2[-1]],
                    color=color2, s=60, zorder=5)
        ax2.annotate(
            f"₹{prices2[-1]:,.0f}",
            xy=(dates2[-1], prices2[-1]),
            xytext=(8, 8),
            textcoords="offset points",
            color=color2,
            fontsize=9,
            fontweight="bold"
        )

        # ── X axis formatting ─────────────────────────────────
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax1.xaxis.set_major_locator(mdates.DayLocator())
        plt.xticks(rotation=45, color="#AAAAAA", fontsize=9)

        # ── Grid ──────────────────────────────────────────────
        ax1.grid(True, color="#333355", linestyle="--",
                 linewidth=0.5, alpha=0.7)
        ax1.set_axisbelow(True)

        # ── Spines ────────────────────────────────────────────
        for spine in ax1.spines.values():
            spine.set_color("#333355")

        # ── Legend (combine both axes) ────────────────────────
        lines1, labels1 = ax1.get_legend_handles_labels()
        if use_dual_axis:
            lines2, labels2 = ax2.get_legend_handles_labels()
        else:
            lines2, labels2 = [], []

        ax1.legend(
            lines1 + lines2,
            labels1 + labels2,
            facecolor="#2A2A3E",
            edgecolor="#333355",
            labelcolor="white",
            fontsize=10,
            loc="upper left"
        )

        # ── Title ─────────────────────────────────────────────
        fig.suptitle(
            f"{label1}  vs  {label2}",
            color="white",
            fontsize=13,
            fontweight="bold"
        )

        if use_dual_axis:
            ax1.set_title(
                "Dual scale — left axis vs right axis",
                color="#AAAAAA",
                fontsize=9,
                pad=4
            )

        plt.tight_layout()

        # ── Save ──────────────────────────────────────────────
        tmp = tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False,
            prefix=f"chart_compare_"
        )
        plt.savefig(
            tmp.name, dpi=150,
            bbox_inches="tight",
            facecolor=fig.get_facecolor()
        )
        plt.close(fig)

        logger.info(f"Comparison chart saved: {tmp.name}")
        return tmp.name

    except Exception as e:
        logger.error(f"generate_comparison_chart failed: {e}")
        return None

def generate_gold_comparison_chart(histories: dict[str, list[dict]]) -> str | None:
    """
    Generate a comparison chart for multiple gold karats.

    Args:
        histories: dict of { "GOLD_24K": [...], "GOLD_22K": [...], ... }
                   Each value is a list of { date, closing_price } dicts.

    Returns:
        Path to saved .png or None.
    """
    # Filter out karats with insufficient data
    valid = {
        k: v for k, v in histories.items()
        if v and len(v) >= 2
    }

    if not valid:
        logger.warning("generate_gold_comparison_chart: no valid data")
        return None

    KARAT_COLORS = {
        "GOLD_24K": "#FFD700",   # bright gold
        "GOLD_22K": "#FFA500",   # orange-gold
        "GOLD_18K": "#CD853F",   # darker gold
    }
    KARAT_LABELS = {
        "GOLD_24K": "Gold 24K",
        "GOLD_22K": "Gold 22K",
        "GOLD_18K": "Gold 18K",
    }

    try:
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#1E1E2E")
        ax.set_facecolor("#1E1E2E")

        for ticker, history in valid.items():
            history = sorted(history, key=lambda x: x["date"])
            dates   = [datetime.strptime(e["date"], "%Y-%m-%d") for e in history]
            prices  = [float(e["closing_price"]) for e in history]

            color = KARAT_COLORS.get(ticker, "#FFFFFF")
            label = KARAT_LABELS.get(ticker, ticker)

            first, last = prices[0], prices[-1]
            change_pct  = ((last - first) / first) * 100
            sign        = "+" if change_pct >= 0 else ""
            full_label  = f"{label}  ({sign}{change_pct:.2f}%)"

            ax.plot(dates, prices, color=color, linewidth=2.5,
                    label=full_label, zorder=3)
            ax.fill_between(dates, prices, min(prices),
                            alpha=0.08, color=color, zorder=2)
            ax.scatter([dates[-1]], [last], color=color, s=60, zorder=5)
            ax.annotate(
                f"₹{last:,.0f}",
                xy=(dates[-1], last),
                xytext=(8, 5),
                textcoords="offset points",
                color=color,
                fontsize=9,
                fontweight="bold"
            )

        # ── X axis ──────────────────────────────────────────
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        plt.xticks(rotation=45, color="#AAAAAA", fontsize=9)
        plt.yticks(color="#AAAAAA", fontsize=9)

        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}")
        )

        # ── Grid & spines ────────────────────────────────────
        ax.grid(True, color="#333355", linestyle="--",
                linewidth=0.5, alpha=0.7)
        ax.set_axisbelow(True)
        for spine in ax.spines.values():
            spine.set_color("#333355")

        # ── Legend ───────────────────────────────────────────
        ax.legend(
            facecolor="#2A2A3E",
            edgecolor="#333355",
            labelcolor="white",
            fontsize=10,
            loc="upper left"
        )

        # ── Title ────────────────────────────────────────────
        karat_names = " vs ".join(KARAT_LABELS.get(k, k) for k in valid)
        fig.suptitle(
            f"Gold Comparison — {karat_names}",
            color="white",
            fontsize=13,
            fontweight="bold"
        )
        ax.set_title(
            "Price per 10g in ₹",
            color="#AAAAAA",
            fontsize=9,
            pad=4
        )

        plt.tight_layout()

        tmp = tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False,
            prefix="chart_gold_compare_"
        )
        plt.savefig(
            tmp.name, dpi=150,
            bbox_inches="tight",
            facecolor=fig.get_facecolor()
        )
        plt.close(fig)

        logger.info(f"Gold comparison chart saved: {tmp.name}")
        return tmp.name

    except Exception as e:
        logger.error(f"generate_gold_comparison_chart failed: {e}")
        return None