from binancess.MarketData import MarketData
from toolss import jsonProcess
import json
import csv
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from toolss import googleDrive
# gauth = GoogleAuth()
# drive = GoogleDrive(gauth)

# data_source = MarketData("ADA")
# googleDrive.upload_to_drive(1642511485000,"ADAUSDT",data_source.getCandlesticksWithLimit("1m","1642511485000",5),drive)

gauth = GoogleAuth()
drive = GoogleDrive(gauth)
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
  print('title: %s, id: %s' % (file1['title'], file1['id']))
file_metadata = {
  'name': 'test_folder',
  'parents': "1X21fyv4EdxngVuZQ2lrk8XcV3PezCNUy",
  'mimeType': 'application/json'
}

folder = drive.CreateFile(file_metadata)
folder.Upload()