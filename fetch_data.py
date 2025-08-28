import numpy as np
import pandas as pd
import sys
import yfinance as yf

from datetime import datetime, timedelta

from tickers import TICKERS

def get_market_data() -> pd.DataFrame:
    start_date = datetime.now() - timedelta(days=6*365)

    historic_data = yf.download(tickers=TICKERS, start=start_date, period='3y', auto_adjust=False, progress=False)

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
    enough_trading_days = adjusted_data.notna().sum() > 700
    active_market_data = adjusted_data.loc[:, enough_trading_days]

    returns = np.log(active_market_data / active_market_data.shift(1)).dropna()
    enough_moving_days = (returns != 0).sum() > 100
    filtered_returns = returns.loc[:, enough_moving_days]

    return filtered_returns
