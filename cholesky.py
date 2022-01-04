import numpy as np
import json
END_POINT = "https://api.binance.us"

def close_column(file):
    f = open(file)
    data = json.load(f)
    s = []
    for i in data:
        s.append(float(i[4]))
    f.close()
    return s

def covariance(x, y):
    mean_x = sum(x)/float(len(x))
    mean_y = sum(y)/float(len(y))
    sub_x = [i - mean_x for i in x]
    sub_y = [i - mean_y for i in y]
    numerator = sum([sub_x[i] * sub_y[i] for i in range(len(sub_x))])
    denominator = len(x) - 1
    cov = numerator / denominator
    return cov

def get_cov_into_matrix(name):
    s = []
    for i in name:
        s.append(close_column(i))
    t = np.array([])
    for i in s:
        u = np.array([])
        for j in s:
            u = np.append(u, covariance(i , j))
        t = np.concatenate((t, np.array(u)))
    return t

def get_cholesky(name):
    arr = get_cov_into_matrix(name)
    L = np.linalg.cholesky(arr)
    return L   