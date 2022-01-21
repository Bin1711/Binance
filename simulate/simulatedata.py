import numpy as np
import pandas as pd
from datetime import datetime
from pmdarima.arima import auto_arima, AutoARIMA
from statsmodels.tsa.arima_model import ARIMA
import statsmodels
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.tsa.api as smt
import math

def fit_sarima(data, order, seasonal_order):
    """
    This function fit the best SARIMA on this data series.

    Parameters
    ----------
    data : pd.series or np.array

    Returns
    -------
    params: The parameters of SARIMA model after being fitted
    """
    arima = statsmodels.tsa.arima.model.ARIMA(endog = data, order=order, seasonal_order = seasonal_order)
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
    tuple: the order of the best SARIMA (p, d, q) (P, D, Q, s)
    Example: (5, 0, 3) (0, 0, 0, 0)
    """
    AUTO = AutoARIMA(max_p = 7, 
                     max_q = 7, 
                     max_P = 3,
                     max_Q = 3,
                     stepwise = False,
                     n_jobs = -1,
                     max_order = None)
    AUTO.fit(data['ret'][1:])
    return AUTO.model_.order, AUTO.model_.seasonal_order 


def simulate_sarima(data, order, seasonal_order, params, number_of_data, number_of_scenario = 1):
    """
    This function returns the simulated data.

    Parameters
    ----------
    data : dataframe
    order: tuple (p,d,q)
    seasonal_order: tuple (P, D, Q, s)
    params: params from fit_sarima()

    Returns
    -------
    simulated data
    """
    arima = statsmodels.tsa.arima.model.ARIMA(endog = data, order=order, seasonal_order = seasonal_order)
    df = arima.simulate(params, number_of_data, repetitions = number_of_scenario)
    df.columns = [a[1] for a in df.columns.to_flat_index()]
    return df.reset_index(drop=True)

def construct_price_series(data, first, first_date, freq):
    """
    This function is required to return the series of close price.

    Parameters
    ----------
    data : data series (which is return data simulated)
    first: first item of the data series
    first_date: first day in the original time series
    freq: frequency of data
    
    Returns
    -------
    data series: the series of close price.
    """
    df = first*(data.shift(1).fillna(0)+1).cumprod()
    df.index = [first_date + i*pd.Timedelta(freq) for i in range(len(df))]
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
    return

def Evaluate_performance(data1, data2, lags = None, style='bmh'):
    """
    Plot the simulated price data vs the actual price.
    Compute autocorrelation and plot the ACF and PACF graph.
    """
    t = len(data2.columns)
    with plt.style.context(style):    
        fig = plt.figure(figsize= (50, 12))
        layout = (3, t + 1)
        data1_ax = plt.subplot2grid(layout, (0, 0))
        data2_ax = plt.subplot2grid(layout, (0, 1))
        acf1_ax = plt.subplot2grid(layout, (1, 0))
        pacf1_ax = plt.subplot2grid(layout, (2, 0))
        
        data1.plot(ax=data1_ax)
        data2.plot(ax=data2_ax)
        data1_ax.set_title('Actual price data')
        data2_ax.set_title('simulated price data')
        plotting_ACF(data1.pct_change(), lags = 30, ax = acf1_ax)
        plotting_PACF(data1.pct_change(), lags = 30, ax = pacf1_ax)  
        for i in range(10):
                acf2_ax = plt.subplot2grid(layout, (1, i + 1))
                pacf2_ax = plt.subplot2grid(layout, (2, i + 1)) 
                plotting_ACF(data2[i].pct_change(), lags = 30, ax = acf2_ax)
                plotting_PACF(data2[i].pct_change(), lags = 30, ax = pacf2_ax)   
    return