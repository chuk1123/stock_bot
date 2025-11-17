"""
Discord Stock Bot
Real-time stock market data bot with candlestick charts and gap analysis
"""
import os
import discord
from discord.ext import commands
from discord.commands import Option
from candle_chart import make_daily_candle_chart, timespan_candle_chart, make_candle_chart
from stock_data import get_ticker_data
from gap_data import get_gap_data
from datetime import datetime, date as d
import pandas as pd
from pytz import timezone
from config import DISCORD_TOKEN, GUILD_IDS, TIMEZONE, MAX_DAYS_HISTORICAL, EXCEL_OUTPUT_FILE

tz = timezone(TIMEZONE)

intents = discord.Intents.default()
bot = commands.Bot(intents=intents)


def df_to_excel(dfs):
    """
    Combine multiple DataFrames and export to Excel.

    Args:
        dfs (list): List of pandas DataFrames to combine
    """
    combined_df = pd.concat(dfs)
    if os.path.exists(EXCEL_OUTPUT_FILE):
        os.remove(EXCEL_OUTPUT_FILE)
    combined_df.to_excel(EXCEL_OUTPUT_FILE, index=False)


@bot.event
async def on_ready():
    """Event handler for bot startup."""
    print(f'We have logged in as {bot.user}')


@bot.slash_command(name="stock_data", description='Get Stock Data in Excel')
async def stock_data(
    ctx,
    ticker: Option(str, description="Stock Symbols (separate with space)", required=True),
    date: Option(str, description='(YYYY-MM-DD)', required=False)
):
    """
    Fetch and export stock data for multiple tickers to Excel.

    Args:
        ticker: Space-separated stock symbols
        date: Date in YYYY-MM-DD format (defaults to today)
    """
    DATAFRAMES = []

    if date is None:
        date = str(datetime.now(tz).date())

    # Validate date is within allowed range
    time_between = d.today() - d(
        int(date.split("-")[0]),
        int(date.split("-")[1]),
        int(date.split("-")[2])
    )

    if time_between.days > MAX_DAYS_HISTORICAL:
        await ctx.respond(f":x: Date may not be longer in the past than {MAX_DAYS_HISTORICAL} days")
        return

    tickers = ticker.split()
    await ctx.send(f"Stocks: {tickers}, Date: {date}")
    await ctx.defer()

    # Fetch data for each ticker
    for ticker_symbol in tickers:
        try:
            response = get_ticker_data(ticker=ticker_symbol, date=date)
        except Exception as err:
            print(f"Error fetching {ticker_symbol}: {err}")
            await ctx.respond(f'Data not found, {ticker_symbol}')
            return

        if response.empty:
            await ctx.respond('Please wait until market close...')
            return

        DATAFRAMES.append(response)

    # Export to Excel and send file
    df_to_excel(DATAFRAMES)
    await ctx.respond(file=discord.File(EXCEL_OUTPUT_FILE))


@bot.slash_command(
    guild_ids=GUILD_IDS,
    description='Get Candle Stick Chart with Timeframe'
)
async def timerange_candle_stick_chart(
    ctx,
    ticker: Option(str, description="Stock Symbols (separate with space)", required=True),
    time1: Option(str, description='Start time (HH:MM)', required=True),
    time2: Option(str, description='End time (HH:MM)', required=True),
    date: Option(str, description='(YYYY-MM-DD)', required=False)
):
    """
    Generate candlestick chart for a specific intraday time range.
    """
    if date is None:
        date = str(datetime.now(tz).date())

    tickers = ticker.split()
    for t in tickers:
        make_candle_chart(t, date, time1, time2)
        await ctx.respond(file=discord.File('timeframe_chart.jpeg'))


@bot.slash_command(
    guild_ids=GUILD_IDS,
    description='Get Daily Candle Stick Chart'
)
async def daily_candle_stick_chart(
    ctx,
    ticker: Option(str, description="Stock Symbols (separate with space)", required=True),
    date: Option(str, description='(YYYY-MM-DD)', required=False)
):
    """
    Generate full-day candlestick chart.
    """
    if date is None:
        date = str(datetime.now(tz).date())

    tickers = ticker.split()
    for t in tickers:
        make_daily_candle_chart(t, date)


@bot.slash_command(name="chart", description='Candle Stick Chart with Time Intervals')
async def chart(
    ctx,
    ticker: Option(str, description="Stock Symbols (separate with space)", required=True),
    timeframe: Option(str, description='minute/hour/day/week', required=True),
    unit: Option(str, description='number of timespans', required=True),
    date: Option(str, description='YYYY-MM-DD', default=None),
    more_data: Option(str, description='yes/no', required=False)
):
    """
    Generate customized candlestick charts with various time intervals.
    """
    if date is None:
        date_obj = datetime.now(tz=tz)
    else:
        date_obj = datetime.fromisoformat(f'{str(date)} 20:00:00')

    more = False
    multiplier = int(unit)
    timespan = timeframe.lower()
    tickers = ticker.split()

    if more_data is not None and more_data.lower() == 'yes':
        more = True

    await ctx.defer()

    for idx, t in enumerate(tickers):
        try:
            ticker_result, date_copy, mult, ts = timespan_candle_chart(
                t, multiplier, timespan, date=date_obj, more_data=more
            )
        except Exception as err:
            print(f"Error generating chart for {t}: {err}")
            await ctx.respond(f'Data not found, {t}')
            return

        if idx == 0:
            await ctx.respond('Charts:')

        chart_filename = f'{ticker_result}-{date_copy}-{mult}{ts}.jpeg'
        await ctx.send(file=discord.File(chart_filename))
        os.remove(chart_filename)


@bot.slash_command(name="gap_stats", description='Get Gap Stats Above Certain Percentage')
async def gap_stats(
    ctx,
    ticker: Option(str, description="Stock Symbol", required=True),
    percent: Option(str, description='Data above this percentage', required=True)
):
    """
    Analyze gap statistics for stocks with gaps above a certain percentage.
    """
    percent_value = int(percent)
    await ctx.defer()

    try:
        results = get_gap_data(ticker, percent_value)
        await ctx.respond(f"Ticker: {ticker} | Percent: {percent_value}")
    except Exception as err:
        print(f"Error getting gap data: {err}")
        await ctx.respond("No Data Found")
        return

    # Extract gap statistics
    dates = results['dates'].iloc[0]
    count = results['count'].iloc[0]
    avg_gap = results['avg_gap'].iloc[0]
    close_greater_open = results['close_greater_open'].iloc[0]
    close_lesser_open = results['close_lesser_open'].iloc[0]
    avg_hod = results['avg_hod'].iloc[0]
    avg_lod = results['avg_lod'].iloc[0]
    avg_high_low = results['avg_high_low'].iloc[0]
    avg_green_performance = results['avg_green_performance'].iloc[0]
    avg_red_performance = results['avg_red_performance'].iloc[0]

    await ctx.send(f"""
----------------------------------------
*Dates*:  {dates}
----------------------------------------
*Count*:  {count}
----------------------------------------
*Avg. Gap*:  {avg_gap}
----------------------------------------
*Close > Open 🟢*:  {close_greater_open}
----------------------------------------
*Close < Open 🔴*:  {close_lesser_open}
----------------------------------------
*Avg. HOD*:  {avg_hod}
----------------------------------------
*Avg. LOD*:  {avg_lod}
----------------------------------------
*Avg. High/Low*:  {avg_high_low}
----------------------------------------
*Avg. 🟢 Performance*:  +{avg_green_performance}
----------------------------------------
*Avg. 🔴 Performance*:  {avg_red_performance}
----------------------------------------
    """)


# Start the bot
bot.run(DISCORD_TOKEN)
