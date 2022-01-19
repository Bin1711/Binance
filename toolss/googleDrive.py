from fileinput import filename
from turtle import title


from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import json


def upload_to_drive(start_time, symbol, data, drive):
    """
        Upload file json to drive under name: symbol_start_time.json

        Parameters:
            startDate: int
                The start UTC+0 Human Time in ms in Unix Timestamp
                Ex: 1642527663000
            symbol: string
                The combination of two cryptos 
                Ex: BTCUSDT
            data: string 
                Data which will be included in file to upload to drive
            drive: GoogleDrive(gauth)
                The connection to drive
     """
    start_time = start_time//60000 * 60000
    fileName = symbol + '_' + str(start_time) +'.json'
    tmpFile = drive.CreateFile({'title': fileName, 'mimeType':'application/json'})
    tmpFile.SetContentString(data)
    tmpFile.Upload()