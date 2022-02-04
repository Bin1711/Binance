from mimetypes import MimeTypes
from turtle import title
import get_data
from toolss import json_process
import json
import csv
from toolss import gdrive
from binancess import upload, market_data

# btc = market_data.MarketData('BTC')
# btc.upload_old_data()

df = get_data.get_data(['BTCUSDT'], '1T', '2020-01-01', '2020-01-02')
# should be of size 1441 x 6
print(df)