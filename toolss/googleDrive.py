from fileinput import filename
from turtle import title


from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import json


def upload_to_drive(start_time, symbol, drive):
    """
        Upload file json to drive under name: symbol_start_time.json

        Parameters:
            startDate: int
                The start UTC+0 Human Time in ms in Unix Timestamp
                Ex: 1642527663000
            symbol: string
                The combination of two cryptos 
                Ex: BTCUSDT
            drive: GoogleDrive(gauth)
                The connection to drive
        """
    def binarySearch(arr, l, r, x):
        if r >= l:
    
            mid = l + (r - l) // 2
    
            # If element is present at the middle itself
            if arr[mid][0] == x:
                return mid
    
            # If element is smaller than mid, then it
            # can only be present in left subarray
            elif arr[mid][0] > x:
                return binarySearch(arr, l, mid-1, x)
    
            # Else the element can only be present
            # in right subarray
            else:
                return binarySearch(arr, mid + 1, r, x)
    
        else:
            # Element is not present in the array
            return r + 1
    start_time = start_time//60000 * 60000
    fileName = symbol + '_' + str(start_time) +'.json'
    tmpFile = drive.CreateFile({'title': fileName, 'mimeType':'application/json'})
    with open ('./' + 'data/' + symbol +'.json',"r") as f:
        tmpJson = json.loads(f.read())
        index = binarySearch(tmpJson,0,len(tmpJson)-1,start_time)
    tmpFile.SetContentString(str(tmpJson[index:]))
    tmpFile.Upload()