from math import gamma
from pandas import DataFrame
import numpy as np

class Backtest:
  FREQ_SYM = {'D': 365, 'H': 24 * 365}

  def __init__(self, alpha, risk_free) -> None:
    self.alpha = alpha
    self.freq = alpha.frequency
    self.syms = alpha.syms
    self.window = alpha.window
    self.trade_per_year = int(self.freq[:-1]) * Backtest.FREQ_SYM[self.freq[-1]]
    self.risk_free = risk_free

  def a_returns(self, data: list) -> float:
    """Returns the annualized data"""
    return data[-1] / self.trade_per_year * len(data)

  def a_stddev(self, data: list) -> float:
    """Returns the annualized standard deviation"""
    return np.std(data) * np.sqrt(self.trade_per_year)

  def sharpe(self, data: list) -> float:
    """Returns the Sharpe Ratio"""
    return (self.a_returns(data) - self.risk_free) / self.a_stddev(data)

  def var(self, data: list, alpha: float) -> float:
    """Returns the VaR"""
    return self.F(data, 1 - alpha)

  def cvar(self, data: list, alpha: float, precision=1000) -> float:
    """Returns the CVaR"""
    dx = np.linspace(0, alpha, precision)
    y = [self.var(data, x) for x in dx]
    return - np.trapz(y, dx) / alpha

  def mdd(self, data: list) -> float:
    """Returns the Maximum Drawdown"""
    intervals = []
    # TODO


  def calmar(self, data: list) -> float:
    """Returns the Calmar Ratio"""
    return (self.a_returns(data) - self.risk_free) / self.mdd(data)

  def test(self, data: DataFrame):
    """Carry out backtest"""
    pass

  def F(data: list, alpha: float):
    """Inverse of Cummulative distribution"""
    return sorted(data)[int(np.ceil(alpha * len(data)) - 1)]