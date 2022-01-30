import numpy as np
import pandas as pd
import json
# END_POINT = "https://api.binance.us"

# def close_column(file):
#     f = open(file)
#     data = json.load(f)
#     s = []
#     for i in data:
#         s.append(float(i[4]))
#     f.close()
#     return s

# def covariance(x, y):
#     mean_x = sum(x)/float(len(x))
#     mean_y = sum(y)/float(len(y))
#     sub_x = [i - mean_x for i in x]
#     sub_y = [i - mean_y for i in y]
#     numerator = sum([sub_x[i] * sub_y[i] for i in range(len(sub_x))])
#     denominator = len(x) - 1
#     cov = numerator / denominator
#     return cov

# def get_cov_into_matrix(name): #sorry, this should be corr instead of cov
#     s = []
#     for i in name:
#         s.append(close_column(i))
#     t = np.array([])
#     for i in s:
#         u = np.array([])
#         for j in s:
#             u = np.append(u, covariance(i , j))
#         t = np.concatenate((t, np.array(u)))
#     return t

# def get_cholesky(name):
#     arr = get_cov_into_matrix(name)
#     L = np.linalg.cholesky(arr)
#     return L

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