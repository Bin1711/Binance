import pandas as pd
import numpy as np
from torch import var
import cholesky
from pandas import DataFrame, read_csv
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from math import sqrt
import simulatedata

def simulate_open_price_and_close (data):
    """This function will simulate 2 series: open price and close price of 1 symbol at the same time

    Params:
        data : Dataframe of a data contains open and close column 

    Returns:
        simulated data
    """
    var_close = compute_std(data['close'])
    mean_close = data['close'].mean()
    var_open = compute_std(data['open'])
    mean_open = data['open'].mean()
    chol = cholesky.cholesky2(data)
    data1 = pd.DataFrame(data, columns = ['time', 'open', 'close'], index='time')
    data1['open'] = normalize_or_standardize_data(data['open'], is_normalize= False) 
    data1['close'] = normalize_or_standardize_data(data['open'], is_normalize= False)
    simulate_corr_rets = pd.DataFrame(np.matmul(chol, data1), index =['open', 'close']).T/100
    res = pd.DataFrame(simulate_corr_rets, columns = ['time', 'open', 'close'], index='time')
    res['open'] = mulback_cholesky(simulate_corr_rets['open',  False, var_open, mean_open])
    res['close'] = mulback_cholesky(simulate_corr_rets['open', False, var_close,  mean_close])
    return res

def compute_std (data):
    # this is just for compute the variance of data
    return sqrt(np.var(data))

def normalize_or_standardize_data(data, is_normalize = True):
    """Normalize data

    Params:
        data: dataframe
        is_normalize: Default: True: normalize data
                      Fault: standardize
    """
    if is_normalize:
        # y = (x - min) / (max - min)
        data = data.reshape((len(data), 1))
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaler = scaler.fit(data)
        res = scaler.transform(data)
        return res
    else:
        # y = (x - mean)/standard deviation
        data = data.reshape((len(data), 1))
        scaler = StandardScaler()
        scaler = scaler.fit(data)
        res = scaler.transform(data)
        return res
        
    
def mulback_cholesky (data, is_normalize = True, x1 =0, x2 = 0):
    """This function is to inverse of nomalization

    Params:
        data: dataframe
        is_normalize: Default: True: apply for normalize data, then x1 = min, x2 = range
                      Fault: aplly for standardize, then x1 = mean, x2 = std
    """
    if is_normalize:
        range = x2
        min = x1
        data1 = data.multiply(range)
        data1 = data1.add(min)
        return data1
    else:
        std = x2
        mean = x1
        data1 = data.multiply(std)
        data1 = data1.add(mean)
        return data1