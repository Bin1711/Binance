from fileinput import filename
import tempfile
from turtle import title


from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import json

gauth = GoogleAuth()
drive = GoogleDrive(gauth)
def upload_to_drive(start_time, symbol, data):
    """
        Upload file json to drive under name: symbol_start_time.json
        Interval is 1m

        Parameters:
            start_time: int
                The start UTC+0 Human Time in ms in Unix Timestamp
                Ex: 1642527663000
            symbol: string
                The combination of two cryptos 
                Ex: BTCUSDT
            data: string 
                Data which will be included in file to upload to drive
     """
    start_time = start_time//60000 * 60000
    fileName = symbol + '_' + str(start_time) +'.json'
    file_list = drive.ListFile({'q': f"title='{fileName}' and trashed=false"}).GetList()
    for file in file_list:
        file.Delete()
    tmpFile = drive.CreateFile({'parents': [{'id': '1X21fyv4EdxngVuZQ2lrk8XcV3PezCNUy'}],'title':fileName,'mimeType':'application/json'})
    tmpFile.SetContentString(data)
    tmpFile.Upload()