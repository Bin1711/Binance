from mimetypes import MimeTypes
from turtle import title
from binancess.market_data import MarketData
from toolss import jsonProcess
import json
import csv
from toolss import gdrive_connection


data_source = MarketData("ADA")
# GoogleDriveConnection.upload_to_drive(1642511485000,"ADAUSDT",data_source.getCandlesticksWithLimit("1m","1642511485000",5))
data_source.upload_old_data()
