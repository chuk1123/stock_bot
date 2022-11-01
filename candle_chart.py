from polygon import RESTClient
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from datetime import time, datetime, timedelta

pio.kaleido.scope.chromium_args = tuple(
    [arg for arg in pio.kaleido.scope.chromium_args if arg != "--disable-dev-shm-usage"])


def multiple_timestamp_to_time(df):
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    df['t_index_only'] = df.timestamp.dt.time
    df.timestamp = df.timestamp.astype(str)
    df.t_index_only = df.t_index_only.astype(str)
    df['timestamp_idx'] = df.t_index_only
    df.set_index('timestamp_idx', inplace=True)


def get_data(ticker, date):
    client = RESTClient("VxaBiHSENdZfJj1Ljm9dpoH5x7LYX1JF")
    aggs2 = client.get_aggs(ticker, 1, "minute", date, date)
    minute_data = pd.DataFrame(aggs2)
    multiple_timestamp_to_time(minute_data)
    '''market_start_idx = minute_data.loc[minute_data.timestamp == '09:30:00'].index[0]
    market_end_idx = minute_data.loc[minute_data.timestamp == '16:00:00'].index[0]
    
    pm_data = minute_data[:market_start_idx]
    ah_data = minute_data[market_end_idx:]'''
    return minute_data


def make_candle_chart(ticker, date, time1, time2):
    time1 += ':00'
    time2 += ':00'
    df = get_data(ticker, date)
    df = df.loc[time1:time2]

    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        title=f'{ticker} {date}')

    fig.write_image('timeframe_chart.jpeg', scale=8)


def make_daily_candle_chart(ticker, date):
    df = get_data(ticker, date)

    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        title=f'{ticker} {date}')

    fig.write_image('daily_chart.jpeg', scale=8)


def timespan_candle_chart(ticker, multiplier, timespan, date, more_data=False):
    date2 = date
    date1 = None
    n = 120
    if more_data:
        n = 165

    if timespan == 'minute':
        date1 = date2

    elif timespan == 'hour':
        date1 = date2 - timedelta(hours=multiplier * n - 1)

    elif timespan == 'day':
        date1 = date2 - timedelta(days=multiplier * n - 1)

    elif timespan == 'week':
        date1 = date2 - timedelta(weeks=multiplier * n - 1)

    date1 = date1.date()
    date2 = date2.date()

    client = RESTClient("VxaBiHSENdZfJj1Ljm9dpoH5x7LYX1JF")

    aggs2 = client.get_aggs(ticker, multiplier, timespan, date1, date2, limit=50000)

    minute_data = pd.DataFrame(aggs2)
    multiple_timestamp_to_time(minute_data)

    date1 = minute_data.head(1).timestamp.item()[:11] #update correct actual date1 after receiving data

    volume_bars = go.Bar(x=minute_data['timestamp'], 
                            y=minute_data.volume, 
                            showlegend=False, 
                            opacity=0.8, 
                            marker={"color": "#3366ff"}, 
                            )

    candlesticks = go.Candlestick(x=minute_data['timestamp'],
                                  open=minute_data['open'],
                                  high=minute_data['high'],
                                  low=minute_data['low'],
                                  close=minute_data['close'], showlegend=False, opacity=1)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
               vertical_spacing=0.03, 
               row_width=[0.2, 0.7])

    fig.add_trace(candlesticks, row=1, col=1)
    fig.add_trace(volume_bars, row=2, col=1)

    fig.update_traces(marker=dict(
            line=dict(width=0)),
            selector=dict(type="bar"))
    
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        title=f'{ticker} {date1} to {date2}',
        #plot_bgcolor="#333333",
        height=1080,
        width=1920,
        template='plotly_dark'
    )

    if timespan == 'minute':
        fig.add_vrect(
            x0=datetime.fromisoformat(f'{str(date2)} 03:59:00'),
            x1=datetime.fromisoformat(f'{str(date2)} 09:30:00'),
            fillcolor="#00EAFF",
            opacity=0.12,
            line_width=0,
        )
        fig.add_vrect(
            x0=datetime.fromisoformat(f'{str(date2)} 16:00:00'),
            x1=datetime.fromisoformat(f'{str(date2)} 20:00:00'),
            fillcolor="red",
            opacity=0.1,
            line_width=0,
        )

    if timespan == 'hour':
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
                dict(bounds=[20, 4], pattern="hour"),  # hide hours outside of 4am-8pm
            ]
        )
    elif timespan == 'day':
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"])  # hide hours outside of 9.30am-4pm
            ]
        )

    fig.write_image(f'{ticker}-{date2}-{multiplier}{timespan}.jpeg', scale=6)

    # print(f'{ticker}-{date2}-{multiplier}{timespan}.jpeg, Success!')

    return ticker, date2, multiplier, timespan

'''from pytz import timezone

tz = timezone('EST')
date = datetime.now(tz)

timespan_candle_chart('REV', 5, 'week', date=date)'''