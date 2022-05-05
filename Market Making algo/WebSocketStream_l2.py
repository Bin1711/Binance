import ssl
import websocket
import _thread as thread
import json

import pandas as pd
import sqlalchemy

def create_df(msg):
    msg = json.loads(msg)
    df = pd.DataFrame(msg['changes'])
    df.iloc[:, 0] = df.iloc[:, 0].astype('str')
    df.iloc[:, 1:] = df.iloc[:, 1:].astype('float')
    df.columns = ['side', 'price', 'volume']
    return df

def on_message(ws, message):
    df = create_df(message)
    try:
        df.to_sql(sym+'_l2', engine, if_exists='fail', index=False, index_label=['side', 'price', 'volume'])
    except:
        pass
    
    df.to_sql('my_tmp_l2', engine, if_exists='replace', index=False, index_label=['side', 'price', 'volume'])
    conn = engine.connect()
    trans = conn.begin()
    
    try:
        engine.execute('delete from '+ sym +'_l2 where price in (select price from my_tmp_l2)')
        trans.commit()
        
        df.drop(df[df['volume']==0].index, inplace = True)
        
        df.to_sql(sym+'_l2', engine, if_exists='append', index=False, index_label=['side', 'price', 'volume'])
    except:
        trans.rollback()
        raise

def on_error(ws, error):
    return
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        ws.send(logon_msg)
    thread.start_new_thread(run, ())

if __name__ == "__main__":
    sym = 'BTCUSD'
    engine = sqlalchemy.create_engine('sqlite:///'+sym+'stream.db')
    inspector = sqlalchemy.inspect(engine)
    
    if sym+'_l2' in inspector.get_table_names():
        engine.execute('delete from '+ sym + '_l2')
        print('reset order book')

    while True:
        sym = 'BTCUSD'
        engine = sqlalchemy.create_engine('sqlite:///'+sym+'stream.db')
        logon_msg = '{"type":"subscribe","subscriptions":[{"name":"l2","symbols":["'+sym+'"]}]}'
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp("wss://api.gemini.com/v2/marketdata",
                                    on_message = on_message,
                                    on_error = on_error,
                                    on_close = on_close,
                                    on_open = on_open)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})