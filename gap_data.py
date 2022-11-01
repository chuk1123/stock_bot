from polygon import RESTClient
import pandas as pd
from datetime import datetime, timedelta
pd.options.mode.chained_assignment = None
from tabulate import tabulate

def multiple_timestamp_to_date(df):
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    df['date'] = df.timestamp.dt.date
    df.timestamp = df.timestamp.dt.time
    
    
    df['date_idx'] = df.date
    df.set_index('date_idx', inplace=True)

def multiple_timestamp_to_time(df):
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    df.timestamp = df.timestamp.dt.time
    df['timestamp_idx'] = df.timestamp.astype(str)
    df.set_index('timestamp_idx', inplace=True)

def get_average_hod_lod_times(ticker, df):
    client = RESTClient("VxaBiHSENdZfJj1Ljm9dpoH5x7LYX1JF")
    hod_df = pd.DataFrame()
    lod_df = pd.DataFrame()
    for i in range(len(df)):
        minute_data = client.get_aggs(ticker, 1, "minute", df.iloc[i].date, df.iloc[i].date)
        minute_data = pd.DataFrame(minute_data)
        multiple_timestamp_to_time(minute_data)
        minute_data = minute_data.loc['09:30:00':'16:00:00']
        hod = minute_data[minute_data.high == df.iloc[i].high]
        lod = minute_data[minute_data.low == df.iloc[i].low]
        hod_df = pd.concat([hod_df, hod], ignore_index=True)
        lod_df = pd.concat([lod_df, lod], ignore_index=True)

    
    hod_times_in_secs = []
    lod_times_in_secs = []

    for i in range(len(hod_df)):
        hod_timestamp = hod_df.iloc[i].timestamp
        hod_seconds = hod_timestamp.hour * 3600 + hod_timestamp.minute * 60
        hod_times_in_secs.append(hod_seconds)

    for i in range(len(lod_df)):
        lod_timestamp = lod_df.iloc[i].timestamp
        lod_seconds = lod_timestamp.hour * 3600 + lod_timestamp.minute * 60
        lod_times_in_secs.append(lod_seconds)

    hod_avg_time_sec = sum(hod_times_in_secs) / len(hod_times_in_secs)
    lod_avg_time_sec = sum(lod_times_in_secs) / len(lod_times_in_secs)

    avg_hod_time = str(timedelta(seconds = hod_avg_time_sec))
    avg_hod_time = avg_hod_time[:5]
    if avg_hod_time[-1] == ':':
        avg_hod_time = avg_hod_time[:4]

    avg_lod_time = str(timedelta(seconds = lod_avg_time_sec))
    avg_lod_time = avg_lod_time[:5]
    if avg_lod_time[-1] == ':':
        avg_lod_time = avg_lod_time[:4]
    
    return avg_hod_time, avg_lod_time

def get_gap_data(ticker, percent):
    client = RESTClient("VxaBiHSENdZfJj1Ljm9dpoH5x7LYX1JF")
    date2 = datetime.today()
    date1 = (date2 - timedelta(days=5000)).date()
    date2 = date2.date()

    day_data = client.get_aggs(ticker, 1, "day", date1, date2)
    day_data = pd.DataFrame(day_data)

    multiple_timestamp_to_date(day_data)
    day_data = day_data[['open', 'close', 'low', 'high', 'date']]
    day_data['prev_close'] = day_data.close.shift(1)
    day_data = day_data[1:]

    day_data['gap'] = day_data.open - day_data.prev_close
    day_data['gap_percent'] = (day_data.open - day_data.prev_close)/day_data.prev_close
    day_data.gap_percent *= 100

    #filter out the gap data that are above a certain gap percentage
    gap_data = day_data[day_data.gap_percent > percent]

    #find the high/low compared to open percentage (then average these values)
    gap_data['high_percent'] = (gap_data.high - gap_data.open)/gap_data.open*100
    gap_data['low_percent'] = (gap_data.low - gap_data.open)/gap_data.open*100
    high_percent_avg = round(gap_data.high_percent.sum()/len(gap_data), 2)
    low_percent_avg = round(gap_data.low_percent.sum()/len(gap_data), 2)

    #find the hod and lod times avgerage
    avg_hod_time, avg_lod_time = get_average_hod_lod_times(ticker, gap_data)

    #find the average gap in dollars and gap percentage
    avg_gap = round((gap_data.gap.sum()/len(gap_data)),2)
    avg_gap_percent = round((gap_data.gap_percent.sum()/len(gap_data)),2)

    #divide the data into red and green performance
    close_higher_data = gap_data[gap_data.open < gap_data.close]
    close_lower_data = gap_data[gap_data.open > gap_data.close]

    #num of green/red days
    num_close_higher = len(close_higher_data)
    num_close_lower = len(close_lower_data)

    #calculate percentage of close compared to open
    close_higher_data['close_percentage'] = (close_higher_data.close - close_higher_data.open) / close_higher_data.open * 100
    close_lower_data['close_percentage'] = (close_lower_data.close - close_lower_data.open) / close_lower_data.open * 100

    #calculate the average close percentages (for green and red performances)
    if close_higher_data.empty:
        avg_green_performance = 0
    else:
        avg_green_performance = round(close_higher_data.close_percentage.sum()/num_close_higher, 2)
    
    if close_lower_data.empty:
        avg_red_performance = 0
    else:
        avg_red_performance = round(close_lower_data.close_percentage.sum()/num_close_lower, 2)


    #find the dates of the gap_data and turn that into string
    dates = gap_data['date'].to_list()
    date_str = ''

    if len(dates) > 10:
        date_str = '(first 10): '
        for i in range(10):
            date_str += str(dates[i])
            date_str += ", "
    else:
        for i in range(len(dates)):
            date_str += str(dates[i])
            date_str += ", "


    results = {
        "dates": date_str,
        "count": len(gap_data),
        "avg_gap": f"${avg_gap} / {avg_gap_percent}%",
        "close_greater_open": f"{num_close_higher} / {round(num_close_higher/len(gap_data), 2) * 100}%",
        "close_lesser_open": f"{num_close_lower} / {round(num_close_lower/len(gap_data), 2) * 100}%",
        "avg_hod": avg_hod_time,
        "avg_lod": avg_lod_time,
        "avg_high_low": f"{high_percent_avg}% / {low_percent_avg}%",
        "avg_green_performance": f"{avg_green_performance}%",
        "avg_red_performance": f"{avg_red_performance}%"
    }

    results = pd.DataFrame(results, index=[0])

    # print(tabulate(results, headers='keys', tablefmt='psql'))

    return results

#get_gap_data('QQQ', 5)