from mimetypes import MimeTypes
from turtle import title
import get_data
from toolss import json_process
import json
import csv
from toolss import gdrive
from binancess import upload, market_data

# GoogleDriveConnection.upload_to_drive(1642511485000,"ADAUSDT",data_source.getCandlesticksWithLimit("1m","1642511485000",5))
# upload.upload_current_data()

df = get_data.get_data(['SOLUSDT'], '1T', 1597125600000, 1597132080000)

# should be of size 109x6
print(df)