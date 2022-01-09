import pandas as pd
import json
import csv
# def jsontocsv(name): 
#     data = pd.read_json('data\json\ADAUSD.json')
#     data.to_csv('data\csv\{name}.csv', index=False)
    
# jsontocsv('ADAUSD')
import json
with open('data/json/BTCUSD.json', 'r') as f:
    dt = json.loads(f.read())

data_file = open('data/csv/BTCUSD.csv', 'w')

csv_writer = csv.writer(data_file)

for i in dt:
    csv_writer.writerow(i)

dt.close() 
data_file.close()

# pdObj = pd.read_json('data\json\ONEUSD.json')
# csvData = dt.to_csv('data\csv\ADAUSD.csv', index=False)
# print(csvData)