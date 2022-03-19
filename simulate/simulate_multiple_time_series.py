from black import T
import pandas as pd
import numpy as np
from torch import t, var
from simulate import cholesky
from pandas import DataFrame, read_csv
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from math import sqrt
from simulate import simulatedata

def simulate_open_and_close (data):
    data1 = pd.DataFrame()
    data1['close'] = data['close']/data['open']
    data1['open'] = data['open']
    dt1 = pd.DataFrame()
    dt1['close'] = data1['close'].pct_change()
    dt1['open'] = data1['open'].pct_change()
    chol = cholesky.cholesky2(data1)
    transform_back = simulate_ret_for_open_and_close (dt1, chol)
    simulated_price_data = pd.DataFrame()
    simulated_price_data['close'] = simulatedata.construct_price_series(transform_back['close'], data1['close'][0], data.index[0], 1)
    simulated_price_data['open'] = simulatedata.construct_price_series(transform_back['open'], data1['open'][0], data.index[0], 1)
    for i in range(len(simulated_price_data['close'])):
        simulated_price_data['close'][i]=simulated_price_data['close'][i] * simulated_price_data['open'][i]
    return simulated_price_data

def simulate_ret_for_open_and_close (data, chol):
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
    # chol = cholesky.cholesky2(data)
    inverse_chol = np.linalg.inv(chol)
    #1st transform
    transform = transform_forward(data, inverse_chol)
    # transform = data
    order_close, seasonal_order_close = simulatedata.get_order(transform['close'][1:])
    order_open, seasonal_order_open = simulatedata.get_order(transform['open'][1:])
    if sum(seasonal_order_close) == 1: seasonal_order_close = (0, 0, 0, 0)
    model_params_close = simulatedata.fit_sarima(transform['close'][1:], order_close, seasonal_order_close)
    if sum(seasonal_order_open) == 1: seasonal_order_open = (0, 0, 0, 0)
    model_params_open = simulatedata.fit_sarima(transform['open'][1:], order_open, seasonal_order_open)
    t_close = simulatedata.simulate_sarima(transform['close'][1:], order_close, seasonal_order_close, model_params_close, len(data), 1)
    t_open = simulatedata.simulate_sarima(transform['open'][1:], order_open, seasonal_order_open, model_params_open, len(data), 1)
    transform_x_chol = pd.DataFrame()
    transform_x_chol['close'] = t_close
    transform_x_chol['open'] = t_open
    # transform_for = transform_forward(transform_x_chol, inverse_chol)
    transform_back_ = transform_back(transform_x_chol, chol, var_close, mean_close, var_open, mean_open)
    return transform_back_

def transform_forward (data, chol_or_inverse_chol):
    data1 = []
    data1 = np.append(data1, normalize_or_standardize_data(data['open'], is_normalize= False))
    data1 = np.append(data1, normalize_or_standardize_data(data['close'], is_normalize= False))
    data1 = data1.reshape(2, len(data['close']))
    data1 = np.matmul(chol_or_inverse_chol, data1)
    simulate_corr_rets = pd.DataFrame(data).copy()
    simulate_corr_rets['close'] = data1[1]
    simulate_corr_rets['open'] = data1[0]
    return simulate_corr_rets

def transform_back(data, chol_or_inverse_chol, var_close, mean_close, var_open, mean_open):
    array = []
    array = np.append(array, data['open'])
    array = np.append(array, data['close'])
    array = array.reshape(2,len(data['close']))
    transform_back = np.matmul(chol_or_inverse_chol, array)
    # transform_back = array
    simulate_corr_rets = pd.DataFrame()
    simulate_corr_rets['open'] = mulback_cholesky(transform_back[0],  False, mean_open, var_open)
    simulate_corr_rets['close'] = mulback_cholesky(transform_back[1],  False, mean_close, var_close)
    return simulate_corr_rets



def compute_mean (data):
    # This is just for compute mean of data
    return data.mean()
    
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
        data1 = data + range
        data1 = data1 + min
        return data1
    else:
        std = x2
        mean = x1
        data1 = data * std
        data1 = data1 + mean
        return data1