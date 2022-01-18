import numpy as np
import pandas as pd
from datetime import datetime
from pmdarima.arima import auto_arima, AutoARIMA
from statsmodels.tsa.arima_model import ARIMA
import statsmodels
import matplotlib.pyplot as plt
import statsmodels.api as sm


def fit_sarima(data, order):
    """
    This function fit the best SARIMA on this data series.

    Parameters
    ----------
    data : pd.series or np.array

    Returns
    -------
    tuple: the order of the best SARIMA (p, d, q) (P, D, Q, s)
    """
    arima = statsmodels.tsa.arima.model.ARIMA(endog = data, order=order, seasonal_order=(4, 0, 3, 30))
    model_fit = arima.fit()
    return model_fit.params

def get_order(data):
    """
    This function returns the order of the time series after fit the return data by fit_arima().

    Parameters
    ----------
    data : dataframe

    Returns
    -------
    tuple: model_order
    Example: (5, 0, 3) 
    """
    AUTO = AutoARIMA()
    AUTO.fit(data['ret'][1:])
    return AUTO.model_.order 


def simulate_sarima(arima, p, d, q, P, D, Q, s, number_of_data):
    t = arima.simulate(p, d, q, P, D, Q, s, number_of_data)
    return t

def construct_price_series(data, first):
    """
    This function is required to return the series of close price.

    Parameters
    ----------
    data : data series (which is return data simulated)
    first: first item of the data series
    
    Returns
    -------
    data series: the series of close price.
    """
    day = data.index[0]
    df = pd.DataFrame({'time':day,'close':first},index='time')
    for i in len(data):
        close = data['ret'][i] * df['close'][i]
        df = df.append(pd.DataFrame({'time': data.index[1], 'close': close}))
    return df

def plotting_ACF(data, lags = None):
    """
    Plot ACF
    
    Parameters:
    ----------
    Data: close price data series
    lags: lags (default: None)
    
    """
    sm.graphics.tsa.plot_acf(data, lags = lags)
    plt.show()
    return

def plotting_PACF(data, lags = None):
    """
    Plot PACF
    
    Parameters:
    ----------
    Data: close price data series
    lags: lags (default: None)
    
    """
    sm.graphics.tsa.plot_pacf(data, lags = lags)
    plt.show()
    return

def Evaluate_performance(data1, data2, lags = None):
    """
    Plot the simulated price data vs the actual price.
    Compute autocorrelation and plot the ACF and PACF graph.
    """
    fig, ax = plt.subplots(1,2,figsize=(10,5))
    data1.close.plot(ax = ax[0])
    data2.close.plot(ax = ax[2])
    plotting_ACF(data2, lags = lags)
    plotting_PACF(data2, lags = lags)   
    return