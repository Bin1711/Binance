from mimetypes import MimeTypes
from turtle import title
from toolss import jsonProcess
import json
import csv
from toolss import gdrive_connection
from binancess import upload, market_data

# GoogleDriveConnection.upload_to_drive(1642511485000,"ADAUSDT",data_source.getCandlesticksWithLimit("1m","1642511485000",5))
upload.upload_old_data()
