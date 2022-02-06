import numpy as np
import pandas as pd

def cholesky(data):
    # Thanh's version
    """
    This function computes cholesky matrix.

    Parameters
    ----------
    data : dict
        This is dictionary data got from function get_data() in get_data.py
    
    Returns
    -------
    cholesky : np.array
        This is cholesky matrix.
    """
    # create new dataframe contains returns of all symbols
    returns_df = pd.DataFrame(columns = data.keys())
    for sym in data.keys():
        returns_df[sym] = data[sym]['close'].pct_change()
    
    # compute correlation matrix
    cov_matrix = returns_df.corr()
    
    # compute cholesky matrix
    cholesky = np.linalg.cholesky(cov_matrix)
    return cholesky

def cholesky2(data):
    # Thanh's version
    """
    This function computes cholesky matrix just for open and close

    Parameters
    ----------
    data : Dataframe
    
    Returns
    -------
    cholesky : np.array
        This is cholesky matrix.
    """
    # create new dataframe contains returns of all symbols
    returns_df = pd.DataFrame(columns = ['open', 'close'])
    for sym in ['open', 'close']:
        returns_df[sym] = data[sym].pct_change()
    
    # compute correlation matrix
    cov_matrix = returns_df.corr()
    
    # compute cholesky matrix
    cholesky = np.linalg.cholesky(cov_matrix)
    return cholesky