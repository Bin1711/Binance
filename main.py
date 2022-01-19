from mimetypes import MimeTypes
from turtle import title
from binancess.MarketData import MarketData
from toolss import jsonProcess
import json
import csv
from toolss import GoogleDriveConnection


data_source = MarketData("ADA")
GoogleDriveConnection.upload_to_drive(1642511485000,"ADAUSDT",data_source.getCandlesticksWithLimit("1m","1642511485000",5))
