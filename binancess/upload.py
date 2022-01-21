# from market_data import MarketData
from binancess.market_data import MarketData
from binancess import const

__all__ = ['upload_old_data', 'upload_current_data']

markets = {c: MarketData(c) for c in const.COINS}

def upload_old_data(start_time: int=0) -> None:
    """
    Upload old data of all markets in const.COINS to drive
    """
    for m in markets.values():
        m.upload_old_data(start_time)


def upload_current_data() -> None:
    """
    Upload data of all markets in const.COINS for the last 60 mins to drive
    """
    for m in markets.values():
        m.upload_current_data()
