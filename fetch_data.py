import sys
import numpy as np
import pandas as pd
import yfinance as yf
from utils import get_upper_triangle_of_matrix

CORRELATION_THRESHOLD = 0.9

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

def get_correlated_pairs(adjusted_data):
    correlation_matrix = adjusted_data.corr(method='pearson')
    triangular_matrix = get_upper_triangle_of_matrix(correlation_matrix)
    pairs = triangular_matrix.stack()
    correlated_pairs = list(pairs[pairs.ge(CORRELATION_THRESHOLD)].index)

    return correlated_pairs