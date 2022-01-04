import pandas as pd

# def jsontocsv(name): 
#     data = pd.read_json('data\json\ADAUSD.json')
#     data.to_csv('data\csv\{name}.csv', index=False)
    
# jsontocsv('ADAUSD')

pdObj = pd.read_json('data\json\ONEUSD.json')
csvData = pdObj.to_csv('data\csv\ADAUSD.csv', index=False)
print(csvData)