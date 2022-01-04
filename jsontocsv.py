import pandas as pd

def jsontocsv(jsonfile): 
    data = pd.read_json()
    data.to_csv('data\BTCUSDT.csv', index=False)