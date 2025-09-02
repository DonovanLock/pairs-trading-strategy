import numpy as np
import pandas as pd
import sys
import yfinance as yf

from datetime import datetime, timedelta

from pairs.pair import Pair
from data.tickers import TICKERS

def get_market_data(tickers: list[str], end_date: datetime) -> pd.DataFrame:
    market_data = yf.download(tickers=tickers, end=end_date, period='3y', auto_adjust=False, progress=False)

    failed_tickers = list(yf.shared._ERRORS.keys())
    if failed_tickers:
        sys.exit('Failed to download market data for: ' + str(failed_tickers))
    
    if 'Adj Close' in market_data.columns:
        adjusted_data = market_data['Adj Close']
    else:
        adjusted_data = market_data['Close']

    return adjusted_data

def get_historic_data() -> pd.DataFrame:
    end_date = datetime.now() - timedelta(days=3*365)
    historic_data = get_market_data(TICKERS, end_date)

    return historic_data

def get_backtesting_data(dependent_stock: str, independent_stock: str) -> pd.DataFrame:
    current_date = datetime.now()
    backtesting_data = get_market_data([dependent_stock, independent_stock], current_date)
    
    return backtesting_data

def get_returns(adjusted_data: pd.DataFrame) -> pd.DataFrame:
    enough_trading_days = adjusted_data.notna().sum() > 700
    active_market_data = adjusted_data.loc[:, enough_trading_days]

    returns = np.log(active_market_data / active_market_data.shift(1)).dropna()
    enough_moving_days = (returns != 0).sum() > 100
    filtered_returns = returns.loc[:, enough_moving_days]

    return filtered_returns

def update_for_backtesting(pair: Pair) -> None:
    backtesting_prices = get_backtesting_data(pair.dependent_stock, pair.independent_stock)
    pair.data = pair.data.reindex(backtesting_prices.index)
    pair.data[pair.dependent_stock] = backtesting_prices[pair.dependent_stock]
    pair.data[pair.independent_stock] = backtesting_prices[pair.independent_stock]
    pair.data['Spread'] = pair.data[pair.dependent_stock] - pair.hedge_ratio * pair.data[pair.independent_stock]