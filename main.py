import os
import time
import discord
from discord.ext import commands
from discord.commands import Option
from candle_chart import make_daily_candle_chart, timespan_candle_chart, make_candle_chart
from stock_data import get_ticker_data
from gap_data import get_gap_data
from datetime import datetime, date as d
import pandas as pd
from pytz import timezone
#from finviz.screener import Screener, NoResults

TOKEN = os.getenv("TOKEN")

tz = timezone('EST')

guild_ids = [985331377698385950, 981996746475462656, 959419758560804894, 905562370326274068, 959872581270388766]

intents = discord.Intents.default()
bot = commands.Bot(intents=intents)

def df_to_excel(dfs):
    combined_df = pd.concat(dfs)
    if os.path.exists('stock_data.xlsx'):
        os.remove('stock_data.xlsx')
        # print('Successfully reset excel file')
    combined_df.to_excel('stock_data.xlsx', index=False)
    return


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
@bot.slash_command(name = "stock_data", description='Get Stock Data in Excel')
async def stock_data(ctx, ticker: Option(str, description="Stock Symbols (separate with space)", required=True),
                     date: Option(str, description='(YYYY-MM-DD)', required=False)):
    DATAFRAMES = []
    if date == None:
        date = str(str(datetime.now(tz).date()))

    time_between = d.today() - d(int(date.split("-")[0]), int(date.split("-")[1]), int(date.split("-")[2]))
    if time_between.days>7:
        await ctx.respond(":x: Date may not be longer in the past than 7 days")
        return
        
    tickers = ticker.split()

    await ctx.send(f"Stocks: {tickers}, Date: {date}")
    await ctx.defer()

    for ticker in tickers:
        # print(ticker, date)
        try:
            response = get_ticker_data(ticker=ticker, date=date)
        except Exception as err:
            print(err)
            await ctx.respond(f'Data not found, {ticker}')
            return

        if response.empty:  # received empty data frame, couldn't get olhc data
            await ctx.respond('Please wait until market close...')
            return

        DATAFRAMES.append(response)

    df_to_excel(DATAFRAMES)

    await ctx.respond(file=discord.File('stock_data.xlsx'))

'''
@bot.slash_command(name = "funda", description = "Get the tickers data")
async def funda(ctx, ticker: Option(str, description="Ticker" , required=True)):
    await ctx.response.defer()

    result = {}
    try:
        res = Screener(tickers=[ticker]).get_ticker_details()[0]
    except NoResults:
        await ctx.send(":x: Ticker not found")
        return

    country = res["Country"]
    market_cap = res["Market Cap"]
    sector = res["Sector"]
    result["Income"] = res["Income"]
    result["Employees"] = res["Employees"]
    result["Insider Own"] = res["Insider Own"]
    result["Insider Trans"] = res["Insider Trans"]
    result["Inst Own"] = res["Inst Own"]
    result["Inst Trans"] = res["Inst Trans"]
    result["Shs Outstand"] = res["Shs Outstand"]
    result["Shs Float"] = res["Shs Float"]
    result["Short Float"] = res["Short Float"]
    result["Avg Volume"] = res["Avg Volume"]

    embeds = [discord.Embed(title=ticker+" ("+country+", "+sector+")", description="**Market Cap**\n" + market_cap)]
    for key, value in result.items():
        embeds[0].add_field(name=key, value=value)

    await ctx.followup.send(embeds=embeds)
'''

@bot.slash_command(guild_ids=guild_ids, description='Get Candle Stick Chart with Timeframe')
async def timerange_candle_stick_chart(ctx, ticker: Option(str, description="Stock Symbols (seperate with space)", required=True), time1: Option(str, description='(HH:MM)', required=True),
                             time2: Option(str, description='(HH:MM)', required=True), date: Option(str, description='(YYYY-MM-DD)', required=False)):
    if date == None:
        date = str(str(datetime.now(tz).date()))

    tickers = ticker.split()
    for t in tickers:
        make_candle_chart(t, date, time1, time2)
        await ctx.respond(file=discord.File('timeframe_chart.jpeg'))

@bot.slash_command(guild_ids=guild_ids, description='Get Daily Candle Stick Chart')
async def daily_candle_stick_chart(ctx, ticker: Option(str, description="Stock Symbols (seperate with space)", required=True), date: Option(str, description='(YYYY-MM-DD)', required=False)):
    if date == None:
        date = str(str(datetime.now(tz).date()))

    tickers = ticker.split()
    for t in tickers:
        make_daily_candle_chart(t, date)


@bot.slash_command(name="chart", description='Candle Stick Chart with Time Intervals')
async def chart(ctx, ticker: Option(str, description="Stock Symbols (separate with space)", required=True),
                timeframe: Option(str, description='minute/hour/day/week', required=True),
                unit: Option(str, description='number of timespans', required=True),
                date: Option(str, description='YYYY-MM-DD', default=None),
                more_data: Option(str, description='yes/no', required=False)):
    if date is None:
        date = datetime.now(tz=tz)
    else:
        date = datetime.fromisoformat(f'{str(date)} 20:00:00')

    more = False
    multiplier = unit
    timespan = timeframe.lower()
    tickers = ticker.split()
    if more_data is not None:
        if more_data.lower() == 'yes':
            more = True
        elif more_data.lower() == 'no':
            more = False

    multiplier = int(multiplier)
    await ctx.defer()
    for idx, t in enumerate(tickers):
        try:
            ticker, date_copy, multiplier, timespan = timespan_candle_chart(t, multiplier, timespan, date=date, more_data=more)  
        except:
            await ctx.respond(f'Data not found, {t}')
            return
        
        if idx == 0:
            await ctx.respond('Charts:')
        await ctx.send(file=discord.File(f'{ticker}-{date_copy}-{multiplier}{timespan}.jpeg'))
        
            
        os.remove(f'{ticker}-{date_copy}-{multiplier}{timespan}.jpeg')




@bot.slash_command(name="gap_stats", description='Get Gap Stats Above Certain Percentage')
async def gap_stats(ctx, ticker: Option(str, description="Stock Symbol", required=True),
                     percent: Option(str, description='Data above this percentage', required=True)):
    percent = int(percent)
    await ctx.defer()
    try:
        results = get_gap_data(ticker, percent)
        await ctx.respond(f"Ticker: {ticker} | Percent: {percent}")
    except:
        await ctx.respond("No Data Found")
        return

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

bot.run(TOKEN)
