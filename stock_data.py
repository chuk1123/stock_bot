"""
Stock Data Module
Fetches stock market data from Polygon.io API
"""
from polygon import RESTClient
import pandas as pd
from datetime import datetime, timedelta
from config import POLYGON_API_KEY

pd.options.mode.chained_assignment = None


def get_ticker_data(ticker, date):
    """
    Fetch comprehensive stock data for a given ticker and date.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        date (str): Date in YYYY-MM-DD format

    Returns:
        pd.DataFrame: DataFrame containing OHLC data, volume, market cap, etc.
    """
    client = RESTClient(POLYGON_API_KEY)

    # Get minute-level aggregate data
    minute_data = client.get_aggs(ticker, 1, "minute", date, date)
    minute_data = pd.DataFrame(minute_data)
    multiple_timestamp_to_time(minute_data)

    # Filter for regular market hours (9:30 AM - 4:00 PM ET)
    daily_data = minute_data.loc['09:30:00':'15:59:00']

    # Verify market is closed (last timestamp should be 15:59)
    if daily_data.tail(1).timestamp.item() != '15:59:00':
        return pd.DataFrame()  # Market not yet closed

    # Calculate daily statistics
    daily_high = daily_data.high.max()
    daily_low = daily_data.low.min()
    daily_open = daily_data.head(1).open.item()
    daily_close = daily_data.tail(1).close.item()

    # Get daily OHLC data
    olhc = client.get_aggs(ticker, 1, "day", date, date)
    olhc = pd.DataFrame(olhc)

    # Get additional metrics
    high_time, low_time = get_high_low_times(minute_data, daily_high, daily_low)
    pm_high, pm_low, pm_vol, pm_high_time, pm_low_time = get_pm_data(minute_data)
    ah_high, ah_low, ah_vol, ah_high_time, ah_low_time = get_ah_data(minute_data)

    # Get ticker details (market cap, shares outstanding)
    ticker_details = client.get_ticker_details(ticker)
    market_cap = ticker_details.market_cap
    weighted_shares_outstanding = ticker_details.weighted_shares_outstanding

    # Build result DataFrame
    df_dict = {
        'ticker': ticker,
        'date': date,
        'open': daily_open,
        'close': daily_close,
        'high': daily_high,
        'low': daily_low,
        'high time': high_time,
        'low time': low_time,
        'volume': olhc.volume.item(),
        'pm high': pm_high,
        'pm low': pm_low,
        'pm high time': pm_high_time,
        'pm low time': pm_low_time,
        'pm volume': pm_vol,
        'ah high': ah_high,
        'ah low': ah_low,
        'ah high time': ah_high_time,
        'ah low time': ah_low_time,
        'ah volume': ah_vol,
        'market cap': market_cap,
        'shares outstanding': weighted_shares_outstanding
    }

    return pd.DataFrame([df_dict])


def multiple_timestamp_to_time(df):
    """
    Convert Unix timestamps to Eastern Time and create time indices.

    Args:
        df (pd.DataFrame): DataFrame with 'timestamp' column in Unix milliseconds
    """
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    df['t_index_only'] = df.timestamp.dt.time
    df.timestamp = df.timestamp.astype(str)
    df.t_index_only = df.t_index_only.astype(str)
    df['timestamp_idx'] = df.t_index_only
    df.set_index('timestamp_idx', inplace=True)


def get_high_low_times(minute_data, daily_high, daily_low):
    """
    Find the times when daily high and low occurred.

    Args:
        minute_data (pd.DataFrame): Minute-level data
        daily_high (float): Daily high price
        daily_low (float): Daily low price

    Returns:
        tuple: (high_time, low_time) as strings
    """
    high_time = minute_data.loc[minute_data['high'] == daily_high].head(1).timestamp.item()
    low_time = minute_data.loc[minute_data['low'] == daily_low].head(1).timestamp.item()
    return high_time, low_time


def get_pm_data(minute_data):
    """
    Get pre-market data (before 9:30 AM ET).

    Args:
        minute_data (pd.DataFrame): Minute-level data

    Returns:
        tuple: (high, low, volume, high_time, low_time)
    """
    pm_data = minute_data.loc[:'09:29:00']

    if pm_data.empty:
        return None, None, None, None, None

    pm_high = pm_data.high.max()
    pm_low = pm_data.low.min()
    pm_vol = pm_data.volume.sum()
    pm_high_time = pm_data.loc[pm_data['high'] == pm_high].head(1).timestamp.item()
    pm_low_time = pm_data.loc[pm_data['low'] == pm_low].head(1).timestamp.item()

    return pm_high, pm_low, pm_vol, pm_high_time, pm_low_time


def get_ah_data(minute_data):
    """
    Get after-hours data (after 4:00 PM ET).

    Args:
        minute_data (pd.DataFrame): Minute-level data

    Returns:
        tuple: (high, low, volume, high_time, low_time)
    """
    ah_data = minute_data.loc['16:00:00':]

    if ah_data.empty:
        return None, None, None, None, None

    ah_high = ah_data.high.max()
    ah_low = ah_data.low.min()
    ah_vol = ah_data.volume.sum()
    ah_high_time = ah_data.loc[ah_data['high'] == ah_high].head(1).timestamp.item()
    ah_low_time = ah_data.loc[ah_data['low'] == ah_low].head(1).timestamp.item()

    return ah_high, ah_low, ah_vol, ah_high_time, ah_low_time
