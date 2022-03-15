import json
from time import time
import pandas as pd
from datetime import datetime, timedelta
from toolss import json_process, gdrive
from binancess.market_data import INTERVAL, FILE_INTERVAL
from binancess.const import TIME_FORMAT
from toolss import convert


def get_data(symbols, frequency: str, start, end = datetime.now(), format=TIME_FORMAT):
    """
    Retrieved the data specified from drive as a DataFrame.

    Parameters
    ----------
    symbols: list of all symbols need to get data.
        Ex: ['BTCUSDT', 'ADAUSDT', 'ETHUSDT']
    frequency: The amount of time between every 2 data points.
        Ex: '15min', '4H', or '1D'
        check this link for more information: 
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    start: The first date (inclusive) that data start. Represented by str, timestamp in ms, or datetime
        Ex: 1597132080000, or datetime.datetime(2020, 8, 11, 7, 48)
    end: The last date (inclusive) that data end. Represented by str, timestamp in ms or datetime. Default is now.
        Ex: 1597125600000, or datetime.datetime(2020, 8, 11, 6, 1)
    format: The format of `start` and `end` if of str type. Default: '%Y-%m-%d'
        Ex: '%Y-%d-%m', '%d/%m/%y %H:%M:%S'
        For more information on the format, check:
            https://www.tutorialspoint.com/python/time_strptime.htm


    Returns
    -------
    data: dictionary of symbols' dataframes. 
        dataframe has datetime index (in UTC) and ['open', 'high', 'low', 'close', 'volume', 'VWAP'] as columns
        /!\ May contains NaN in VWAP columns
        Ex: {'BTCUSDT': dataframe,
             'ADAUSDT': dataframe,
             'ETHUSDT': dataframe}

    """
    start, start_time = _parse_time(start, format)
    end, end_time = _parse_time(end, format)

    start = start // FILE_INTERVAL * FILE_INTERVAL
    end_time += timedelta(seconds=30)

    data = {}
    for symbol in symbols:
        data[symbol] = _download_data(symbol, start, end)
        data[symbol] = _fit_data_to_df(data[symbol], frequency)[start_time:end_time]
    return data


def _download_data(symbol: str, start: int, end: int):
    """
    Download data from drive to a json file. For arguments, see `get_data`
    """
    data = ''
    t = start
    while t <= end:
        file = gdrive.get_file(time=t, symbol=symbol)
        if file is None:
            print('file not found:', symbol, convert.timestampms_to_utc(t))
            t += FILE_INTERVAL
            continue
        if t == start:
            data = file.GetContentString()
        else:
            data = data[:-1] + ',' + file.GetContentString()[1:]

        t += FILE_INTERVAL
    return data


def _fit_data_to_df(data, frequency: str):
    """
    Parse the json file into a DataFrame. For arguments, see `get_data`
    """
    
    df = json.loads(data)
    df = pd.DataFrame(df, columns = 
                        ['time', 'open', 'high', 'low', 'close', 
                        'volume', 'Close time', 'Quote asset volume', 
                        'Number of trades', 'Taker buy base asset volume', 
                        'Taker buy quote asset volume', 'Ignore'])
    df.drop(columns = ['Close time', 'Quote asset volume', 
                        'Number of trades', 'Taker buy base asset volume', 
                        'Taker buy quote asset volume', 'Ignore'], inplace = True)

    
    df[:] = df[:].astype('float64')
    df['time'] = pd.to_datetime(df['time'], unit='ms', utc=True)
    
    #grouped data to with frequency
    new_df = pd.DataFrame()
    new_df['open'] = df.groupby(pd.Grouper(key = 'time', freq = frequency))['open'].first()
    new_df['high'] = df.groupby(pd.Grouper(key = 'time', freq = frequency))['high'].max()
    new_df['low'] = df.groupby(pd.Grouper(key = 'time', freq = frequency))['low'].min()
    new_df['close'] = df.groupby(pd.Grouper(key = 'time', freq = frequency))['close'].last()
    new_df['volume'] = df.groupby(pd.Grouper(key = 'time', freq = frequency))['volume'].sum()
    
    df['vol x close'] = df['close']*df['volume']
    new_df['VWAP'] = df.groupby(pd.Grouper(key = 'time', freq = frequency))['vol x close'].sum()/new_df['volume']
    
    new_df.fillna(method='ffill', inplace = True)
    #drop nan
    # new_df.dropna(inplace = True)

    return new_df


def _parse_time(time, format):
    """Parse the time into timestamp in ms and datetime"""
    if type(time) == datetime:
        timestamp = int(time.timestamp() * 1000)
        dt = time
    elif type(time) == str:
        dt = datetime.strptime(time, format)
        timestamp = int(dt.timestamp() * 1000)
    else:
        timestamp = time
        dt = datetime.utcfromtimestamp(time / 1000)
    return timestamp, dt









