from binancess.MarketData import MarketData
from toolss import jsonProcess
import json
import csv
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from toolss import googleDrive
gauth = GoogleAuth()
drive = GoogleDrive(gauth)
googleDrive.upload_to_drive(1641356603000,"ADAUSDT",drive)