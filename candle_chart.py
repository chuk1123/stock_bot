"""
Candlestick Chart Module
Generates candlestick charts using Plotly and Polygon.io data
"""
from polygon import RESTClient
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from datetime import time, datetime, timedelta
from config import POLYGON_API_KEY, CHART_OUTPUT_FILE, DAILY_CHART_OUTPUT_FILE

# Configure Kaleido for chart rendering
pio.kaleido.scope.chromium_args = tuple(
    [arg for arg in pio.kaleido.scope.chromium_args if arg != "--disable-dev-shm-usage"]
)


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


def get_data(ticker, date):
    """
    Fetch minute-level stock data for charting.

    Args:
        ticker (str): Stock ticker symbol
        date (str): Date in YYYY-MM-DD format

    Returns:
        pd.DataFrame: Minute-level OHLCV data
    """
    client = RESTClient(POLYGON_API_KEY)
    aggs = client.get_aggs(ticker, 1, "minute", date, date)
    minute_data = pd.DataFrame(aggs)
    multiple_timestamp_to_time(minute_data)
    return minute_data


def make_candle_chart(ticker, date, time1, time2):
    """
    Create candlestick chart for a specific time range.

    Args:
        ticker (str): Stock ticker symbol
        date (str): Date in YYYY-MM-DD format
        time1 (str): Start time in HH:MM format
        time2 (str): End time in HH:MM format
    """
    minute_data = get_data(ticker, date)
    data = minute_data.loc[time1:time2]

    # Create candlestick and volume subplot
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{ticker} - {date}', 'Volume'),
        row_width=[0.2, 0.7]
    )

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data['timestamp'],
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='OHLC'
        ),
        row=1, col=1
    )

    # Add volume bars
    fig.add_trace(
        go.Bar(x=data['timestamp'], y=data['volume'], name='Volume'),
        row=2, col=1
    )

    # Update layout
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.write_image(CHART_OUTPUT_FILE)


def make_daily_candle_chart(ticker, date):
    """
    Create full-day candlestick chart (9:30 AM - 4:00 PM ET).

    Args:
        ticker (str): Stock ticker symbol
        date (str): Date in YYYY-MM-DD format
    """
    minute_data = get_data(ticker, date)
    data = minute_data.loc['09:30:00':'16:00:00']

    # Create candlestick and volume subplot
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{ticker} - {date}', 'Volume'),
        row_width=[0.2, 0.7]
    )

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data['timestamp'],
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='OHLC'
        ),
        row=1, col=1
    )

    # Add volume bars
    fig.add_trace(
        go.Bar(x=data['timestamp'], y=data['volume'], name='Volume'),
        row=2, col=1
    )

    # Update layout
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.write_image(DAILY_CHART_OUTPUT_FILE)


def timespan_candle_chart(ticker, time1, time2, date):
    """
    Create candlestick chart for custom timespan.

    Args:
        ticker (str): Stock ticker symbol
        time1 (str): Start time in HH:MM format
        time2 (str): End time in HH:MM format
        date (str): Date in YYYY-MM-DD format
    """
    minute_data = get_data(ticker, date)
    data = minute_data.loc[time1:time2]

    # Create candlestick chart
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data['timestamp'],
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close']
            )
        ]
    )

    fig.update_layout(title=f'{ticker} - {date} ({time1} to {time2})')
    fig.write_image(CHART_OUTPUT_FILE)
