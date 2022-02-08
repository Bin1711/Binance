from black import T
import pandas as pd
import numpy as np
from torch import t, var
from simulate import cholesky
from pandas import DataFrame, read_csv
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from math import sqrt


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
    data1 = []
    data1 = np.append(data1, normalize_or_standardize_data(data['open'], is_normalize= False))
    data1 = np.append(data1, normalize_or_standardize_data(data['close'], is_normalize= False))
    data1 = data1.reshape(len(data['close']), 2)
    # data1['open'] = normalize_or_standardize_data(data['open'], is_normalize= False) 
    # data1['close'] = normalize_or_standardize_data(data['close'], is_normalize= False)
    data1 = np.transpose(np.matmul(data1, chol))
    simulate_corr_rets = pd.DataFrame(data)
    simulate_corr_rets['close'] = data1[1]
    simulate_corr_rets['open'] = data1[0]
    simulate_corr_rets['open'] = mulback_cholesky(simulate_corr_rets['open'],  False, var_open, mean_open)
    simulate_corr_rets['close'] = mulback_cholesky(simulate_corr_rets['close'], False, var_close,  mean_close)
    return simulate_corr_rets

def compute_std (data):
    # this is just for compute the std of data
    return sqrt(np.var(data))

def normalize_or_standardize_data(data, is_normalize = True):
    """Normalize data

    Params:
        data: dataframe
        is_normalize: Default: True: normalize data
                      Fault: standardize
    """
    std = compute_std(data)
    mean = data.mean()
    if is_normalize:
        # y = (x - min) / (max - min)
        data = data.values.resize((0, 2))
        data = data.reshape((-1, 1))
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaler = scaler.fit(data)
        res = scaler.transform(data)
        return res
    else:
        # y = (x - mean)/standard deviation
        # values = data.values
        # values = values.reshape((len(data), 1))
        # scaler = StandardScaler()
        # scaler = scaler.fit(values)
        # res = scaler.transform(values)
        res = []
        for i, j in enumerate(data):
            res.append((j - mean)/ std)
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