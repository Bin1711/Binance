from tracemalloc import start
import requests
import json
import os.path
from datetime import datetime
from binancess.const import TIME_FORMAT
from toolss import convert, gdrive, json_process
import math

ENDPOINT = "https://api.binance.com"
INTERVALS = {
    'm': 60 * 1000,
    'h': 3600 * 1000,
    'd': 24 * 3600 * 1000,
    'w': 7 * 24 * 3600 * 1000,
    'M': 30 * 7 * 24 * 3600 * 1000 
    }
INTERVAL = INTERVALS['m']
FILE_INTERVAL = INTERVALS['w']

class MarketData: 
    def __init__(self, from_symbol: str,to_symbol: str="USDT"):
        """ 
        Source of Data for exchanging rate between a couple of assets(cryto and forex). If there is only one parameter, it is assumed that this will be converted to USD.
        
        Parameters:
            from_symbol: The symbol of Crypto to be converted
            to_symbol: The symbol of Crypto convert to (default: 'USDT')
        """
        self.from_symbol, self.to_symbol = from_symbol, to_symbol
        self.symbol = from_symbol + to_symbol


    def get_filename(self, time):
        if type(time) == int:
            time = convert.timestampms_to_utc(time)
        return self.symbol + '_' + time 


    def get_candlesticks_with_limit(self, interval: str,start_time: int, end_time: int=-1, limit: int=1000) -> str:
        """
        Get Candles Data From API In An Specific Interval With Limit 1000 Candle

        Parameters:
            interval: The interval of an candlestick (time unit is 'm', 'h', 'd', 'w', 'M')
                Eg: "1m","5m","1h","5h","1d","1w", "12M"
            start_time: The start UTC+0 Human Time in type: timestamp format
            end_time: The end Human UTC+0 Time in type: timestamp format (default: now)
            limit: The maximum number of candlesticks
        
        Return:
            text in json type
        """
        if end_time == -1:
            end_time = int(datetime.now().timestamp()) * 1000
        start_time, end_time = str(start_time), str(end_time)
        endpoint = ENDPOINT + "/api/v3/klines"
        url = f'{endpoint}?symbol={self.symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit={limit}'
        
        payload={}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        
        return response.text

   
    def get_candlesticks(self, interval: str='1m', start_time: int=0, end_time: int=-1, filename: str=None):
        """
        Get Candles Data From API In An Specific Interval and write into the specified filename
        /!\ Delete existing file

        Parameters:
            interval: 
                The interval of an candlestick ("1m","5m","1h","5h","1d","1m","1y")
            start_time: The start UTC+0 Human Time in ms in Unix Timestamp
                Ex: 1642527663000
            end_time: The start UTC+0 Human Time in ms in Unix Timestamp, "now" for now
                Ex: 1642527663000, "now"
                Default: "now"
            filename: Name of file to be written into (path: ./data/{filename}.json)
                Ex: "BTCUSDT"
                Default: {self.data_file}
        """
        if end_time == -1:
            end_time = int(datetime.now().timestamp()) * 1000

        if filename is None:
            filename = self.symbol

        try:
            interval_time = int(interval[:-1]) * INTERVALS[interval[-1]]
        except:
            print('Invalid Interval')
            return
        
        path = './data/'+filename+".json"
        if os.path.exists(path):
            os.remove(path)

        while start_time < end_time:
            response_text = self.get_candlesticks_with_limit(interval, start_time, end_time)
            tmp = json.loads(response_text)
            if len(tmp) == 0:
                break

            start_time = tmp[len(tmp)-1][0] + interval_time
            if os.path.exists(path): 
                json_process.deleteLastCharacterInJsonFile(filename)
                json_process.transferDataToJsonFile(","+response_text[1:], filename)
            else:
                json_process.transferDataToJsonFile(response_text, filename)

        return filename


    def getRecentTrade(self):
        """
        Return new trade in text in json type
        """
        endPoint = ENDPOINT + "/api/v3/trades"
        url = endPoint + "?symbol=" + self.from_symbol + self.to_symbol 
        
        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.text


    def upload_old_data(self, start_time: int=0) -> None:
        """
        Upload old data of this market to drive
        """
        end_time = (int(datetime.now().timestamp()) * 1000) // FILE_INTERVAL * FILE_INTERVAL
        
        resp = json.loads(self.get_candlesticks_with_limit('1m', start_time, end_time, 60))
        if len(resp) == 0:
            return
        start_time = resp[0][0] // FILE_INTERVAL * FILE_INTERVAL

        while start_time < end_time:
            utctime = convert.timestampms_to_utc(start_time)
            tofile = self.get_filename(utctime)
            exists = gdrive.get_file(tofile + ".json")
            if exists is not None:
                print('skipping file', utctime, ' ' * 10)
                start_time += FILE_INTERVAL
                continue
            
            print('uploading', self.symbol, utctime, end='\r')
            fromfile = self.get_candlesticks('1m', start_time, start_time + FILE_INTERVAL - INTERVAL // 2)

            if os.path.getsize('./data/' + fromfile + '.json') < 100:
                print(f'empty response at {utctime} for {fromfile}, please try again later')
                break

            gdrive.upload_file_to_drive(fromfile, tofile)
            start_time += FILE_INTERVAL

        print('uploaded', self.symbol, 'until time', convert.timestampms_to_utc(end_time, '%Y-%m-%d %H:%M:%S'), ' ' * 10)

    
    def upload_current_data(self):
        """
        Upload data of this market for the last {FILE_INTERVAL} to drive
        """
        start_time = int(datetime.now().timestamp() * 1000 - 2 * FILE_INTERVAL)
        start_time = start_time // FILE_INTERVAL * FILE_INTERVAL
        gdrive.delete_file(None , start_time, self.from_symbol + self.to_symbol)
        gdrive.delete_file(None , start_time + FILE_INTERVAL, self.from_symbol + self.to_symbol)
        gdrive.delete_file(None , start_time + 2 * FILE_INTERVAL, self.from_symbol + self.to_symbol)
        self.upload_old_data(start_time)


### DEVELOPING
    def realTimeUpdating(self): 
        tmpEndDate = str(int(datetime.now().timestamp())*1000)
        while True: 
            self.get_candlesticks("1m","")
### DEVELOPING


### Need to comment
    def testCandleData(self):
        flag = True
        ErrorIndex = -1
        with open ("./data/"+self.from_symbol+self.to_symbol+".json") as f: 
            tmp = json.loads(f.read())
        for i in range(len(tmp)-1):
            if tmp[i+1][0] - tmp[i][0] != 60000:
                flag = False
                ErrorIndex = i
                break
        return flag, ErrorIndex
### Need to comment


