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

  def a_returns(self, returns: list) -> float:
    """Returns the annualized returns"""
    return returns[-1] / self.trade_per_year * len(returns)

  def a_stddev(self, returns: list) -> float:
    """Returns the annualized standard deviation"""
    return np.std(returns) * np.sqrt(self.trade_per_year)

  def sharpe(self, returns: list) -> float:
    """Returns the Sharpe Ratio"""
    return (self.a_returns(returns) - self.risk_free) / self.a_stddev(returns)

  def var(self, returns: list, alpha: float) -> float:
    """Returns the VaR"""
    pass

  def cvar(self, returns: list, alpha: list) -> float:
    """Returns the CVaR"""
    pass

  def mdd(self, returns: list) -> float:
    """Returns the Maximum Drawdown"""
    pass

  def calmar(self, returns: list) -> float:
    """Returns the Calmar Ratio"""
    pass

  def test(self, data: DataFrame):
    """Carry out backtest"""
    pass

  def F(data: list, alpha: float):
    """Inverse of Cummulative distribution"""
    return sorted(data)[int(np.ceil(alpha * len(data)) - 1)]