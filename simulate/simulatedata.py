import numpy as np
import pandas as pd
from datetime import datetime
from pmdarima.arima import auto_arima, AutoARIMA
from statsmodels.tsa.arima_model import ARIMA
import statsmodels
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.tsa.api as smt


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
    arima = statsmodels.tsa.arima.model.ARIMA(endog = data, order=order)
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


def simulate_sarima(data, order, p, d, q, P, D, Q, s, number_of_data):
    arima = statsmodels.tsa.arima.model.ARIMA(endog = data, order=order)
    t = arima.simulate(p, d, q, P, D, Q, s, number_of_data)
    return t

def construct_price_series(data, first, day):
    """
    This function is required to return the series of close price.

    Parameters
    ----------
    data : data series (which is return data simulated)
    first: first item of the data series
    day: first day in the original time series
    
    Returns
    -------
    data series: the series of close price.
    """
    df = pd.DataFrame({'time':day,'close':first},index='time')
    for i in len(data):
        close = data['ret'][i] * df['close'][i]
        df = df.append(pd.DataFrame({'time': data.index[i], 'close': close}))
    return df

def plotting_ACF(data, lags = None, ax = None):
    """
    Plot ACF
    
    Parameters:
    ----------
    Data: close price data series
    lags: lags (default: None)
    
    """
    sm.graphics.tsa.plot_acf(data, lags = lags, ax = ax)
    plt.show()
    return

def plotting_PACF(data, lags = None, ax = None):
    """
    Plot PACF
    
    Parameters:
    ----------
    Data: close price data series
    lags: lags (default: None)
    
    """
    sm.graphics.tsa.plot_pacf(data, lags = lags, ax = ax)
    plt.show()
    return

def Evaluate_performance(data1, data2, lags = None, figsize=(10, 8), style='bmh'):
    """
    Plot the simulated price data vs the actual price.
    Compute autocorrelation and plot the ACF and PACF graph.
    """
    with plt.style.context(style):    
        fig = plt.figure(figsize=figsize)
        layout = (3, 2)
        data1_ax = plt.subplot2grid(layout, (0, 0))
        data2_ax = plt.subplot2grid(layout, (0, 1))
        acf1_ax = plt.subplot2grid(layout, (1, 0))
        pacf1_ax = plt.subplot2grid(layout, (2, 0))
        acf2_ax = plt.subplot2grid(layout, (1, 1))
        pacf2_ax = plt.subplot2grid(layout, (2, 1))
        
        data1.plot(ax=data1_ax)
        data2.plot(ax=data2_ax)
        data1_ax.set_title('Actual price data')
        data2_ax.set_title('simulated price data')
        plotting_ACF(data2, lags = lags, ax = acf1_ax)
        plotting_PACF(data2, lags = lags, ax = pacf1_ax)   
        plotting_ACF(data2, lags = lags, ax = acf2_ax)
        plotting_PACF(data2, lags = lags, ax = pacf2_ax)   
    return