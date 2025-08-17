import numpy as np
import pandas as pd
import statsmodels.api as sm
import sys
import yfinance as yf

from statsmodels.tsa.stattools import adfuller, coint

from config import COINTEGRATION_THRESHOLD, CORRELATION_THRESHOLD, ROLLING_WINDOW
from utils import get_upper_triangle_of_matrix

def get_market_data(tickers: list[str]) -> pd.DataFrame:
    historic_data = yf.download(tickers=tickers, period='3y', auto_adjust=False, progress=False)

    failed_tickers = list(yf.shared._ERRORS.keys())
    if failed_tickers:
        sys.exit('Failed to download market data for: ' + str(failed_tickers))

    # for this to work with a vpn, i need to switch country every time it runs?
    if 'Adj Close' in historic_data.columns:
        adjusted_data = historic_data['Adj Close']
    else:
        adjusted_data = historic_data['Close']

    return adjusted_data

def get_returns(adjusted_data: pd.DataFrame) -> pd.DataFrame:
    returns = np.log(adjusted_data / adjusted_data.shift(1)).dropna()
    return returns

def get_correlated_pairs(returns: pd.DataFrame) -> list[tuple[str, str]]:
    correlation_matrix = returns.corr(method='pearson')
    triangular_matrix = get_upper_triangle_of_matrix(correlation_matrix)
    pairs = triangular_matrix.stack()
    correlated_pairs = list(pairs[pairs.ge(CORRELATION_THRESHOLD)].index)

    return correlated_pairs

def get_cointegrated_pairs(correlated_pairs: list[tuple[str, str]], market_data: pd.DataFrame) -> list[tuple[list[str], pd.DataFrame]]:
    # list of cointegrated pairs and a cleaned dataframe containing their returns
    cointegrated_pairs = []
    for pair in correlated_pairs:
        stock1 = market_data[pair[0]]
        stock2 = market_data[pair[1]]
        aligned_stocks = pd.concat([stock1, stock2], axis=1)
        cleaned_stocks = aligned_stocks.replace([np.inf, -np.inf], np.nan).dropna()

        if len(cleaned_stocks) == 0:
            continue

        # Engle-Granger two-step cointegration test
        cointegration_test = coint(cleaned_stocks[pair[0]], cleaned_stocks[pair[1]])
        p_value = cointegration_test[1]

        if p_value <= COINTEGRATION_THRESHOLD:
            # there exists some beta (hedge ratio) such that
            # stock1 - beta * stock2 is a stationary series
            cointegrated_pairs.append([pair, cleaned_stocks])

    return cointegrated_pairs

def calculate_hedge_ratio(dependent_stock: pd.Series, independent_stock: pd.Series) -> float:
    X = sm.add_constant(independent_stock)
    model = sm.OLS(dependent_stock, X).fit()

    # dependent_stock = constant + hedge_ratio * independent_stock + epsilon,
    # where epsilon is a stationary series. As a result,
    # dependent_stock - hedge_ratio * independent_stock is stationary
    hedge_ratio = model.params[independent_stock.name]

    return hedge_ratio

def get_hedge_ratios(stock1_data: pd.Series, stock2_data: pd.Series) -> tuple[float, float]:

    beta1 = calculate_hedge_ratio(stock1_data, stock2_data)
    beta2 = calculate_hedge_ratio(stock2_data, stock1_data)    

    return beta1, beta2

def get_best_spread(stock1: str, stock2: str, pair_data: pd.DataFrame, hedge_ratios: tuple[float, float]) -> tuple[pd.Series, float, float, str, str]:

    spread1 = pair_data[stock1] - hedge_ratios[0] * pair_data[stock2]
    spread2 = pair_data[stock2] - hedge_ratios[1] * pair_data[stock1]

    p_value1 = adfuller(spread1)[1]
    p_value2 = adfuller(spread2)[1]

    if p_value1 < p_value2:
        return spread1, p_value1, hedge_ratios[0], stock1, stock2
    else:
        return spread2, p_value2, hedge_ratios[1], stock2, stock1

def get_z_score(spread: pd.Series) -> pd.Series:
    rolling_mean = spread.rolling(window=ROLLING_WINDOW).mean()
    rolling_stdev = spread.rolling(window=ROLLING_WINDOW).std()
    z_score = (spread - rolling_mean) / rolling_stdev
    return z_score