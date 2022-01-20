from tracemalloc import start
import requests
import json
import os.path
from requests.models import REDIRECT_STATI
from toolss import gdrive_connection as gdrive, jsonProcess
import datetime
ENDPOINT = "https://api.binance.com"
class MarketData: 
    def __init__(self, from_symbol,to_symbol = "USDT"):
        """ 
        Source of Data for exchanging rate between a couple of assets(cryto and forex). If there is only one parameter, it is assumed that this will be converted to USD.
        
        Parameters:
            from_symbol: The symbol of Crypto to be converted
            to_symbol: The symbol of Crypto convert to (default: 'USDT')
        """
        self.from_symbol = from_symbol
        self.to_symbol = to_symbol
        self.symbol = from_symbol + to_symbol
        self.candlesticks_intervals = {
            'm': 60 * 1000,
            'h': 3600 * 1000,
            'd': 24 * 3600 * 1000,
            'w': 7 * 24 * 3600 * 1000,
            'M': 30 * 7 * 24 * 3600 * 1000 
        }


    def get_candlesticks_with_limit(self, interval: str,start_time: int, limit: int=1000, end_time: int=-1) -> str:
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
            end_time = int(datetime.datetime.now().timestamp()) * 1000
        start_time, end_time = str(start_time), str(end_time)
        endpoint = ENDPOINT + "/api/v3/klines"
        url = endpoint + "?symbol=" + self.from_symbol + self.to_symbol + "&" +"interval=" + interval +"&startTime=" + start_time  +"&endTime=" + end_time +"&limit=" + str(limit)
        
        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        
        return response.text

   
    def get_candlesticks(self, start_time, end_time=None, interval=None, filename=None):
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
        if end_time is None:
            end_time = int(datetime.datetime.now().timestamp()) * 1000

        if filename is None:
            filename = self.from_symbol + self.to_symbol

        if interval is None:
            interval = '1m'

        try:
            interval_time = int(interval[:-1]) * self.candlesticks_intervals[interval[-1]]
        except:
            print('Invalid Interval')
            return
        
        path = './data/'+filename+".json"
        if os.path.exists(path):
            os.remove(path)

        while start_time < end_time:
            response_text = self.get_candlesticks_with_limit(interval,start_time,end_time)
            tmp = json.loads(response_text)
            
            if len(tmp) == 0: 
                break
            
            tmp_end_time = tmp[len(tmp)-1][0]
            start_time = tmp_end_time + interval_time
            if os.path.exists(path): 
                jsonProcess.deleteLastCharacterInJsonFile(self.from_symbol+self.to_symbol)
                jsonProcess.transferDataToJsonFile(","+response_text[1:],self.from_symbol+self.to_symbol)
            else:
                jsonProcess.transferDataToJsonFile(response_text,self.from_symbol+self.to_symbol)


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


    def upload_old_data(self) -> None:
        """
        Upload old data of this market to drive
        """
        interval = 60 * 1000
        end_time = int(datetime.datetime.now().timestamp()) * 1000
        
        resp = json.loads(self.get_candlesticks_with_limit('1m', 0, 5))
        if len(resp) == 0:
            return
        start_time = resp[0][0] // interval * interval

        while start_time < end_time:
            exists = gdrive.get_file(start_time, self.symbol)
            if exists is not None:
                exists = json.loads(exists.GetContentString())
                if len(exists) != 0:
                    print('skipping file', start_time)
                    start_time = exists[-1][0] + 60000
                    continue

            resp = self.get_candlesticks_with_limit('1m', start_time, 60, end_time)
            body = json.loads(resp)
            ### At sometime, Binance do not give us data, so length of body can be 0. If we encounter this case, the function will end  
            if len(body) == 0:
                break
            ###
            gdrive.upload_to_drive(start_time, self.symbol, resp)

            start_time = body[-1][0] + interval

    
    def upload_current_data(self):
        """
        Upload data of this market for the last 60 mins to drive
        """
        interval = self.candlesticks_intervals['m']
        end_time = int(datetime.datetime.now().timestamp()) // 60 * 60 * 1000
        start_time = end_time - 60 * self.candlesticks_intervals['m']

        while start_time < end_time:
            resp = self.get_candlesticks_with_limit('1m', start_time, 60, end_time)
            body = json.loads(resp)

            if len(body) == 0:
                break

            gdrive.upload_to_drive(start_time, self.symbol, resp)

            start_time = body[-1][0] + interval 

### DEVELOPING
    def realTimeUpdating(self): 
        tmpEndDate = str(int(datetime.datetime.now().timestamp())*1000)
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