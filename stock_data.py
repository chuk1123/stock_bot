from polygon import RESTClient
import pandas as pd
from datetime import datetime, timedelta
pd.options.mode.chained_assignment = None


def get_ticker_data(ticker, date):
    client = RESTClient("VxaBiHSENdZfJj1Ljm9dpoH5x7LYX1JF")

    minute_data = client.get_aggs(ticker, 1, "minute", date, date)

    minute_data = pd.DataFrame(minute_data)
    multiple_timestamp_to_time(minute_data)

    daily_data = minute_data.loc['09:30:00':'15:59:00']

    if daily_data.tail(1).timestamp.item() != '15:59:00':
        # print('Market not closed')
        return pd.DataFrame()

    daily_high = daily_data.high.max()
    daily_low = daily_data.low.min()
    daily_open = daily_data.head(1).open.item()
    daily_close = daily_data.tail(1).close.item()

    olhc = client.get_aggs(ticker, 1, "day", date, date)
    olhc = pd.DataFrame(olhc)

    high_time, low_time = get_high_low_times(minute_data, daily_high, daily_low)
    pm_high, pm_low, pm_vol, pm_high_time, pm_low_time = get_pm_data(minute_data)
    outstanding_shares, market_cap = get_outstanding_shares_market_cap(ticker, date)
    high_of_1m, high_of_5m, low_of_5m = get_other_data(minute_data)
    low_before_12, low_after_12 = get_low_before_after_12(minute_data)
    # insider_own, inst_own, shs_float, short_float = get_finviz_data(ticker)

    processed_aggs = {
        'outstanding_shares': f'{outstanding_shares / 1_000_000}',
        'market_cap': f'{market_cap / 1_000_000}',
        # 'float': shs_float,
        # 'institutional_ownership': inst_own,
        # 'short_float': short_float,
        # 'insider_ownership': insider_own,
        'prev_close': get_prev_close(ticker, date),
        'open': daily_open,
        'high': daily_high,
        'low': daily_low,
        'close': daily_close,
        'volume': f'{olhc.volume.item() / 1_000_000}',
        'high_time': high_time,
        'low_time': low_time,
        'high_of_1m': high_of_1m, 'high_of_5m': high_of_5m, 'low_of_5m': low_of_5m,
        'low_before_12': low_before_12, 'low_after_12': low_after_12,
        'pm_high': pm_high,
        'pm_low': pm_low,
        'pm_vol': f'{pm_vol}',
        'pm_high_time': pm_high_time,
        'pm_low_time': pm_low_time
    }

    final_data = pd.DataFrame(processed_aggs, index=[0])

    final_data.insert(0, 'date', date)
    final_data.insert(1, 'ticker', ticker)
    final_data['day_of_week'] = get_weekday(date)

    # print(final_data)

    return final_data  # Success


def get_weekday(date):
    year, month, day = (int(x) for x in str(date).split('-'))
    return datetime(year, month, day).strftime('%A')


def get_prev_day(date):
    year, month, day = (int(x) for x in str(date).split('-'))
    date2 = datetime(year, month, day).date()
    if date2.weekday() == 0:
        return str((datetime(year, month, day) - timedelta(days=3)).date())
    else:
        return str((datetime(year, month, day) - timedelta(days=1)).date())


def get_prev_close(ticker, date):
    client = RESTClient("VxaBiHSENdZfJj1Ljm9dpoH5x7LYX1JF")
    prev_day = get_prev_day(date)
    prev_data = client.get_daily_open_close_agg(ticker, prev_day)
    return prev_data.close


def get_outstanding_shares_market_cap(ticker, date):
    client = RESTClient("VxaBiHSENdZfJj1Ljm9dpoH5x7LYX1JF")
    ticker_details = client.get_ticker_details(ticker, date)
    return ticker_details.weighted_shares_outstanding, ticker_details.market_cap


def get_high_low_times(minute_data, daily_high, daily_low):
    high_time_data = minute_data[minute_data.high == float(daily_high)]
    low_time_data = minute_data[minute_data.low == float(daily_low)]

    try:
        high_time = high_time_data.tail(1)['timestamp'].item()
    except:
        high_time = 'N/A'

    try:
        low_time = low_time_data.tail(1)['timestamp'].item()
    except:
        low_time = 'N/A'

    return high_time, low_time


def get_pm_data(minute_data):
    try:
        pm_data = minute_data[:'09:30:00']
        pm_vol = pm_data.volume.sum()

        pm_high = pm_data['high'].max()
        pm_low = pm_data['low'].min()

        pm_high_data, pm_low_data = pm_data[pm_data['high'] == pm_high], pm_data[pm_data['low'] == pm_low]

        pm_high_time, pm_low_time = pm_high_data.tail(1).timestamp.item(), pm_low_data.tail(1).timestamp.item()
        return pm_high, pm_low, pm_vol / 1_000_000, pm_high_time, pm_low_time

    except:
        return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'


def multiple_timestamp_to_time(df):
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    df.timestamp = df.timestamp.dt.time
    df.timestamp = df.timestamp.astype(str)
    df['timestamp_idx'] = df.timestamp
    df.set_index('timestamp_idx', inplace=True)


def get_other_data(minute_data):
    try:
        data_1m = minute_data.loc['09:30:00':'09:31:00']
        data_1m_high = data_1m.high.max()
    except:
        data_1m_high = 'N/A'
    try:
        data_5m = minute_data.loc['09:30:00':'09:35:00']
        data_5m_high, data_5m_low = data_5m.high.max(), data_5m.low.min()
    except:
        data_5m_high = 'N/A'
        data_5m_low = 'N/A'

    return data_1m_high, data_5m_high, data_5m_low


def get_low_before_after_12(minute_data):
    try:
        before_12 = minute_data['09:30:00':'12:00:00']
        after_12 = minute_data['12:00:00':'16:00:00']
        low_before_12 = before_12.low.min().item()
        low_after_12 = after_12.low.min().item()
        return low_before_12, low_after_12
    except:
        return 'N/A', 'N/A'
