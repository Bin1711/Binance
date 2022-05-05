import ssl
import websocket
import json

import pandas as pd
import sqlalchemy

def create_df(msg):
    msg = json.loads(msg)
    if len(msg['events']) > 0:
        df = pd.DataFrame(msg['events'])
        df['timestampms'] = msg['timestampms']
        df = df[['timestampms', 'price', 'amount', 'makerSide']]
        #df['timestampms'] = df['timestampms'].astype('int') #pd.to_datetime(df['timestampms'], unit='ms')
        df['price'] = df['price'].astype('float')
        df['amount'] = df['amount'].astype('float')
        df['makerSide'] = df['makerSide'].astype('str')
        return df

def on_message(ws, message):
    df = create_df(message)
    if df is not None:
        df.to_sql(sym+'_traded', engine, if_exists='append', index=False, index_label=['timestampms', 'price', 'amount', 'makerSide'])

def on_close(ws):
    print("### closed ###")

if __name__ == "__main__":
    while True:
        sym = 'LTCUSD'
        engine = sqlalchemy.create_engine('sqlite:///'+sym+'stream.db')
        
        ws = websocket.WebSocketApp(
            "wss://api.gemini.com/v1/marketdata/btcusd?trades=true",
            on_message=on_message,
            on_close = on_close)
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})