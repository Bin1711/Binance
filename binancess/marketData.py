import requests
import time, datetime
END_POINT = "https://api.binance.us"
class marketData: 
    def __init__(self, symbol,eSymbol):
        """ 
        :param symbol: The symbol of Cryto to be converted
        :param eSymbol: The symbol of Cryto convert to
        """
        self.symbol = symbol
        self.eSymbol = eSymbol
   
    def getCandlesticks(self, interval,startDate, endDate="now"):
        """
        Get Candles Data In An Specific Interval
        :param interval: Frequency of requesting data
        :param startDate: The start UTC+0 Human Time in type: dd/mm/yy
        :param endDate: The end Human UTC+0 Time in type: dd/mm/yy (default: now)
        :return: return text in json type
        """
        tmpStartDate = str(int(time.mktime(datetime.datetime.strptime(startDate, "%d/%m/%Y").timetuple()))*1000)
        if endDate == "now":
            tmpEndDate = str(int(datetime.datetime.now().timestamp())*1000)
        else:
            tmpEndDate = str(int(time.mktime(datetime.datetime.strptime(endDate, "%d/%m/%Y").timetuple()))*1000)
        endPoint = END_POINT + "/api/v3/klines"
        url = endPoint + "?symbol=" + self.symbol + self.eSymbol + "&" +"interval=" + interval +"&startTime=" + tmpStartDate +"&endTime=" + tmpEndDate
        
        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.text
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