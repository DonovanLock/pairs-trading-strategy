import numpy as np
import pandas as pd
import sys
import yfinance as yf

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
