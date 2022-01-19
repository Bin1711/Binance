from binancess.MarketData import MarketData
from toolss import jsonProcess
END_POINT = "https://api.binance.us"
# #TRASH API
# API_KEY= "BlauCq9caQqSBHp1txb8eR2QYbay3U9xqnzrLn6EqOo1A7D7PIFwAsw8mZL47bvj"
# API_SIGN ="GKe8xqlfynUq3ALvK4r0V628knVD6V53Qo3dC9Jd5iczbeSLrVyKbMKx8eP5GCJw"
# #TRASH API
# dataSoure = marketData("BTC","USDT")
# data = dataSoure.getCandlesticks("1d","20/12/2021","21/12/2021")
# data_txt = jsonProcess.printj(data)
def data_to_json(name, interval,startDate, endDate="now" ):
    dataSoure = MarketData(name,"USDT")
    data = dataSoure.getCandlesticks(interval,startDate, endDate)
    data_txt = jsonProcess.printj(data)
    jsonProcess.createNewJsonDataFile(name)
    jsonProcess.transferDataToJsonFile(data,"./data/" + name + ".json")
    
    