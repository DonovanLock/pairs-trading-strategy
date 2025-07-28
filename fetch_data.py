import sys
import pandas as pd
from statsmodels.tsa.stattools import coint
import numpy as np
import yfinance as yf
from utils import get_upper_triangle_of_matrix

CORRELATION_THRESHOLD = 0.6
COINTEGRATION_THRESHOLD = 0.05

def get_market_data(tickers):
    historic_data = yf.download(tickers=tickers, period='3y', auto_adjust=False, progress=False)

    failed_tickers = list(yf.shared._ERRORS.keys())
    if failed_tickers:
        sys.exit("Failed to download market data for: " + str(failed_tickers))

    #for this to work with a vpn, i need to switch country every time it runs?
    if 'Adj Close' in historic_data.columns:
        adjusted_data = historic_data['Adj Close']
    else:
        adjusted_data = historic_data['Close']

    return adjusted_data

def get_returns(adjusted_data):
    returns = np.log(adjusted_data / adjusted_data.shift(1)).dropna()
    return returns

def get_correlated_pairs(returns):
    correlation_matrix = returns.corr(method='pearson')
    triangular_matrix = get_upper_triangle_of_matrix(correlation_matrix)
    pairs = triangular_matrix.stack()
    correlated_pairs = list(pairs[pairs.ge(CORRELATION_THRESHOLD)].index)

    return correlated_pairs

def get_cointegrated_pairs(correlated_pairs, market_data):
    cointegrated_pairs = []
    for pair in correlated_pairs:
        stock1 = market_data[pair[0]]
        stock2 = market_data[pair[1]]
        aligned_stocks = pd.concat([stock1, stock2], axis=1)
        cleaned_stocks = aligned_stocks.replace([np.inf, -np.inf], np.nan).dropna()

        if len(cleaned_stocks) == 0:
            continue

        cointegration_test = coint(cleaned_stocks.iloc[:, 0], cleaned_stocks.iloc[:, 1])
        p_value = cointegration_test[1]

        if p_value <= COINTEGRATION_THRESHOLD:
            cointegrated_pairs.append(pair)
        
    return cointegrated_pairs
