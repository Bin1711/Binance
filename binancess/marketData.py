import requests
import json
import os.path
from requests.models import REDIRECT_STATI
from toolss import jsonProcess
import time, datetime
END_POINT = "https://api.binance.com"
class MarketData: 
    def __init__(self, symbol,eSymbol = "USDT"):
        """ 
        Source of Data for exchanging rate between a couple of assets(cryto and forex). If there is only one parameter, it is assumed that this will be converted to USD.
        :param symbol: The symbol of Cryto to be converted
        :param eSymbol: The symbol of Cryto convert to (default: USD)
        """
        self.symbol = symbol
        self.eSymbol = eSymbol
        self.dataFile = symbol + eSymbol


    def getCandlesticksWithLimit(self, interval,startDate, limit=1000, endDate="now"):
        """
        Get Candles Data From API In An Specific Interval With Limit 1000 Candle
        :param interval: The interval of an candlestick ("1m","5m","1h","5h","1d","1m","1y")
        :param startDate: The start UTC+0 Human Time in type: timestamp format
        :param endDate: The end Human UTC+0 Time in type: timestamp format (default: now)
        :param limit: The maximum number of candlesticks
        :return: return text in json type
        """
        if endDate == "now":
            endDate = int(datetime.datetime.now().timestamp()) * 1000
        startDate, endDate = str(startDate), str(endDate)
        endPoint = END_POINT + "/api/v3/klines"
        url = endPoint + "?symbol=" + self.symbol + self.eSymbol + "&" +"interval=" + interval +"&startTime=" + startDate  +"&endTime=" + endDate +"&limit=" + str(limit)
        
        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        
        return response.text

   
    def getCandlesticks(self, startDate, endDate=None, interval=None, filename=None):
        """
        Get Candles Data From API In An Specific Interval and write into the specified filename
        /!\ Delete existing file

        Parameters:
            interval: 
                The interval of an candlestick ("1m","5m","1h","5h","1d","1m","1y")
            startDate: int
                The start UTC+0 Human Time in ms in Unix Timestamp
                Ex: 1642527663000
            endDate: int
                The start UTC+0 Human Time in ms in Unix Timestamp, "now" for now
                Ex: 1642527663000, "now"
                Default: "now"
            filename: string
                Name of file to be written into (path: ./data/{filename}.json)
                Ex: "BTCUSDT"
                Default: {self.symbol + self.eSymbol}
        """
        if endDate is None:
            endDate = int(datetime.datetime.now().timestamp()) * 1000

        if filename is None:
            filename = self.symbol + self.eSymbol

        if interval is None:
            interval = '1m'
        
        path = './data/'+filename+".json"
        if os.path.exists(path):
            os.remove(path)

        while startDate < endDate:
            responseText = self.getCandlesticksWithLimit(interval,startDate,endDate)
            tmp = json.loads(responseText)
            
            if len(tmp) == 0: 
                break
            
            tmpEndDate = tmp[len(tmp)-1][0]
            startDate = tmpEndDate + 60000
            if os.path.exists(path): 
                jsonProcess.deleteLastCharacterInJsonFile(self.symbol+self.eSymbol)
                jsonProcess.transferDataToJsonFile(","+responseText[1:],self.symbol+self.eSymbol)
            else:
                jsonProcess.transferDataToJsonFile(responseText,self.symbol+self.eSymbol)


    def getRecentTrade(self):
        """
        :return: return new trade in text in json type
        """
        endPoint = END_POINT + "/api/v3/trades"
        url = endPoint + "?symbol=" + self.symbol + self.eSymbol 
        
        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.text




        

### DEVELOPING
    def realTimeUpdating(self): 
        tmpEndDate = str(int(datetime.datetime.now().timestamp())*1000)
        while True: 
            self.getCandlesticks("1m","")
### DEVELOPING


### Need to comment
    def testCandleData(self):
        flag = True
        ErrorIndex = -1
        with open ("./data/"+self.symbol+self.eSymbol+".json") as f: 
            tmp = json.loads(f.read())
        for i in range(len(tmp)-1):
            if tmp[i+1][0] - tmp[i][0] != 60000:
                flag = False
                ErrorIndex = i
                break
        return flag, ErrorIndex
### Need to comment