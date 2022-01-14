from quickstart import gauth
from pydrive.drive import GoogleDrive
from zipfile import ZipFile
from io import BytesIO
import json
import pandas as pd
from datetime import datetime

drive = GoogleDrive(gauth)
''' just ignore this
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
    print('title: %s, id: %s' % (file1['title'], file1['id']))
'''  
zipp = drive.CreateFile({'id':'1YTeNkGWkihHYNV-8D2F7zABEWiC20ZyN'})
toUnzipStringContent = zipp.GetContentString(encoding='cp862')
toUnzipBytesContent = BytesIO(toUnzipStringContent.encode('cp862'))

def get_data(syms, frequency, start, end = datetime.now()):
    """
    This function collects data from drive.

    Parameters
    ----------
    syms : list
        list of all symbols need to get data.
        Ex: ['BTCUSDT', 'ADAUSDT', 'ETHUSDT']
    frequency : str
        The amount of time between every 2 data points.
        Ex: '15min', '4H', or '1D'
        check this link for more information: 
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    start : str or datetime
        The first date (inclusively) that data start.
        Ex: 'YYYY-MM-DD', or 'DD-MM-YYYY', or datetime.datetime(year, month, date, hour, min, second)
    end : str or datetime
        The last date (inclusively) that data end. Default is now.
        Ex: 'YYYY-MM-DD', or 'DD-MM-YYYY', or datetime.datetime(year, month, date, hour, min, second)

    Returns
    -------
    data : dict
        dictionary of symbols' dataframes.
        Ex:
            {'BTCUSDT': dataframe,
             'ADAUSDT': dataframe,
             'ETHUSDT': dataframe}
        dataframe has datetime index (in UTC) and ['open', 'high', 'low', 'close', 'volume', 'VWAP'] as columns
    """
    data = {}
    with ZipFile(toUnzipBytesContent, 'r') as zip_ref:
        all_paths = set(zip_ref.namelist())
        for sym in syms:
            if 'data/' + sym + '.json' not in all_paths:
                print('There is no {sym} data in database.'.format(sym = sym))
                continue
            else:
                with zip_ref.open('data/'+'BTCUSDT.json', 'r') as f:
                    df = json.loads(f.read())
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
            
                    #drop nan
                    new_df.dropna(inplace = True)
                    data[sym] = new_df[start:end]
    return data