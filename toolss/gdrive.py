from datetime import datetime
from fileinput import filename
import tempfile
from turtle import title

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import json
from binancess.const import TIME_FORMAT

gauth = GoogleAuth()
drive = GoogleDrive(gauth)
def upload_to_drive(start_time: int, symbol: str, data:str ):
    """
    Upload file json to drive under name: symbol_start_time.json
    Interval is 1m

    Parameters:
        start_time: The start UTC+0 Human Time in ms in Unix Timestamp
            Ex: 1642527663000
        symbol: The combination of two cryptos 
            Ex: BTCUSDT
        data: JSON data which will be included in file to upload to drive
            Ex: '[]'
     """
    start_time = start_time//60000 * 60000
    file_name = symbol + '_' + str(start_time) +'.json'
    file_list = drive.ListFile({'q': f"title='{file_name}' and trashed=false"}).GetList()
    for file in file_list:
        file.Delete()
    tmp_file = drive.CreateFile({'parents': [{'id': '1X21fyv4EdxngVuZQ2lrk8XcV3PezCNUy'}],'title':file_name,'mimeType':'application/json'})
    tmp_file.SetContentString(data)
    tmp_file.Upload()



def upload_file_to_drive(fromfile: str, tofile: str):
    fromfile += '.json'
    tofile += '.json'
    file_list = drive.ListFile({'q': f"title='{tofile}' and trashed=false"}).GetList()
    for file in file_list:
        file.Delete()
    tmp_file = drive.CreateFile({'parents': [{'id': '1X21fyv4EdxngVuZQ2lrk8XcV3PezCNUy'}],'title':tofile,'mimeType':'application/json'})
    tmp_file.SetContentFile(f'./data/{fromfile}')
    tmp_file.Upload()



def get_file(utctime, symbol: str):
    """
    Get existing records of `upload_to_drive`
    """
    if type(utctime) == int:
        utctime = datetime.utcfromtimestamp(utctime // 1000).strftime(TIME_FORMAT)
    filename = symbol + '_' + utctime +'.json'
    file_list = drive.ListFile({'q': f"title='{filename}' and trashed=false"}).GetList()
    return file_list[0] if len(file_list) != 0 else None