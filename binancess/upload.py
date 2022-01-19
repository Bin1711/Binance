from market_data import MarketData
import const

def upload_to_drive():
    for c in const.COINS:
        data = MarketData(c)
        data.upload_old_data()