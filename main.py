from mimetypes import MimeTypes
from turtle import title
import get_data
from datetime import datetime
from toolss import gdrive
from binancess import upload, market_data
from toolss import json_process
from toolss import convert
# btc = market_data.MarketData('BTC')
# btc.upload_old_data()
# btc.upload_current_data()

# should be of size 1441 x 6
upload.upload_current_data()