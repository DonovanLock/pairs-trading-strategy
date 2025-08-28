import pandas as pd
import sys

from config import ANNUAL_TRADING_DAYS, PORTFOLIO_PORTION_INVESTED_PER_TRADE, RISK_FREE_RATE, STARTING_CAPITAL
from pair import Pair
from trading_signals import Position, Signal

#reminder: dependent stock - hedge ratio * independent stock = stationary spread
#z_score < -ENTRY_THRESHOLD -> go long on spread -> buy dependent stock, sell independent stock
#z_score > ENTRY_THRESHOLD -> go short on spread -> sell dependent stock, buy independent stock

def get_position_value(long_stock: float, short_stock: float, long_shares: float,
                       short_shares: float, short_entry_price: float) -> float:
    long_market_value = long_stock * long_shares
    short_market_value = ((2 * short_entry_price) - short_stock) * short_shares
    return long_market_value + short_market_value


def update_invested_capital(pair: Pair, date: pd.Timestamp) -> None:
    position = Position[pair.data['Position'][date]]
    if position == Position.LONG:
        pair.invested_capital = get_position_value(pair.data[pair.dependent_stock][date],
                                                   pair.data[pair.independent_stock][date],
                                                   pair.long_shares, pair.short_shares,
                                                   pair.short_entry_price)
    elif position == Position.SHORT:
        pair.invested_capital = get_position_value(pair.data[pair.independent_stock][date],
                                                   pair.data[pair.dependent_stock][date],
                                                   pair.long_shares, pair.short_shares,
                                                   pair.short_entry_price)

def enter_position(investment_sum: float, pair: Pair, date: pd.Timestamp, backtesting: pd.DataFrame) -> None:
    backtesting.loc[date, 'Entries'] += 1
    position = Position[pair.data['Position'][date]]
    pair.invested_capital = investment_sum
    dependent_stock_price = pair.data[pair.dependent_stock][date]
    independent_stock_price = pair.data[pair.independent_stock][date]

    if position == Position.LONG:
        pair.long_shares = investment_sum / (dependent_stock_price + pair.hedge_ratio * independent_stock_price)
        pair.short_shares = pair.hedge_ratio * pair.long_shares
        pair.short_entry_price = independent_stock_price

    elif position == Position.SHORT:
        pair.short_shares = investment_sum / (dependent_stock_price + pair.hedge_ratio * independent_stock_price)
        pair.long_shares = pair.hedge_ratio * pair.short_shares
        pair.short_entry_price = dependent_stock_price

def exit_position(pair: Pair, uninvested_capital: float, date: pd.Timestamp, backtesting: pd.DataFrame) -> float:
    backtesting.loc[date, 'Exits'] += 1
    new_uninvested_capital = uninvested_capital + pair.invested_capital
    pair.invested_capital = pair.long_shares = pair.short_shares = pair.short_entry_price = 0
    return new_uninvested_capital

def simulate_day(pair: Pair, date: pd.Timestamp, backtesting: pd.DataFrame, uninvested_capital: float) -> float:
    signal = Signal[pair.data['Signal'][date]]

    match (signal):
        case (Signal.NONE):
            update_invested_capital(pair, date)
            return uninvested_capital

        case (Signal.ENTER_LONG | Signal.ENTER_SHORT):
            investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * uninvested_capital
            enter_position(investment_sum, pair, date, backtesting)
            return uninvested_capital - investment_sum
        
        case (Signal.EXIT_LONG | Signal.EXIT_SHORT):
            update_invested_capital(pair, date)
            return exit_position(pair, uninvested_capital, date, backtesting)
        
        case (Signal.EXIT_LONG_AND_ENTER_SHORT | Signal.EXIT_SHORT_AND_ENTER_LONG):
            update_invested_capital(pair, date)
            new_uninvested_capital = exit_position(pair, uninvested_capital, date, backtesting)
            investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * new_uninvested_capital
            enter_position(investment_sum, pair, date, backtesting)
            return new_uninvested_capital - investment_sum

def perform_backtest(pairs: list[Pair]) -> pd.DataFrame:
    if not all(pair.data['Signal'].index.equals(pairs[0].data['Signal'].index) for pair in pairs[1:]): #this should never happen
        sys.exit('All spreads must have the same index for backtesting.')

    backtesting = pd.DataFrame(index=pairs[0].data['Signal'].dropna().index)
    backtesting['Capital'] = pd.Series(index=backtesting.index, dtype=float)
    backtesting['Entries'] = 0
    backtesting['Exits'] = 0
    uninvested_capital = STARTING_CAPITAL

    for i in backtesting.index:
        for pair in pairs:
            uninvested_capital = simulate_day(pair, i, backtesting, uninvested_capital)
            """
            position = Position[pair.data['Position'][i]]
            signal = Signal[pair.data['Signal'][i]]
            dependent_stock_price = pair.data[pair.dependent_stock][i]
            independent_stock_price = pair.data[pair.independent_stock][i]

            if signal == Signal.NONE:
                if position == Position.LONG:
                    pair.invested_capital = get_invested_capital(dependent_stock_price,
                                                                 independent_stock_price,
                                                                 pair.long_shares, pair.short_shares,
                                                                 pair.short_entry_price)
                elif position == Position.SHORT:
                    pair.invested_capital = get_invested_capital(independent_stock_price,
                                                                 dependent_stock_price,
                                                                 pair.long_shares, pair.short_shares,
                                                                 pair.short_entry_price)

            elif signal == Signal.ENTER_LONG:
                investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * uninvested_capital
                pair.long_shares, pair.short_shares, pair.short_entry_price = enter_position(investment_sum, dependent_stock_price,
                                                                          independent_stock_price, pair.hedge_ratio, signal)
                pair.invested_capital = investment_sum
                uninvested_capital -= investment_sum
                backtesting.loc[i, 'Entries'] += 1
            
            elif signal == Signal.ENTER_SHORT:
                investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * uninvested_capital
                pair.long_shares, pair.short_shares, pair.short_entry_price = enter_position(investment_sum, dependent_stock_price,
                                                                          independent_stock_price, pair.hedge_ratio, signal)
                pair.invested_capital = investment_sum
                uninvested_capital -= investment_sum
                backtesting.loc[i, 'Entries'] += 1
            
            elif signal == Signal.EXIT_LONG:
                pair.invested_capital = get_invested_capital(dependent_stock_price,
                                                             independent_stock_price,
                                                             pair.long_shares, pair.short_shares,
                                                             pair.short_entry_price)
                uninvested_capital += pair.invested_capital
                pair.invested_capital = pair.long_shares = pair.short_shares = pair.short_entry_price = 0
                backtesting.loc[i, 'Exits'] += 1
                
            elif signal == Signal.EXIT_SHORT:
                pair.invested_capital = get_invested_capital(independent_stock_price,
                                                             dependent_stock_price,
                                                             pair.long_shares, pair.short_shares,
                                                             pair.short_entry_price)
                uninvested_capital += pair.invested_capital
                pair.invested_capital = pair.long_shares = pair.short_shares = pair.short_entry_price = 0
                backtesting.loc[i, 'Exits'] += 1
            
            elif signal == Signal.EXIT_LONG_AND_ENTER_SHORT:
                pair.invested_capital = get_invested_capital(dependent_stock_price,
                                                             independent_stock_price,
                                                             pair.long_shares, pair.short_shares,
                                                             pair.short_entry_price)
                uninvested_capital += pair.invested_capital
                
                investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * uninvested_capital
                pair.long_shares, pair.short_shares, pair.short_entry_price = enter_position(investment_sum, dependent_stock_price,
                                                                          independent_stock_price, pair.hedge_ratio, signal)
                pair.invested_capital = investment_sum
                uninvested_capital -= investment_sum
                backtesting.loc[i, 'Entries'] += 1
                backtesting.loc[i, 'Exits'] += 1
            
            else:
                pair.invested_capital = get_invested_capital(independent_stock_price,
                                                             dependent_stock_price,
                                                             pair.long_shares, pair.short_shares,
                                                             pair.short_entry_price)
                uninvested_capital += pair.invested_capital
                
                investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * uninvested_capital
                pair.long_shares, pair.short_shares, pair.short_entry_price = enter_position(investment_sum, dependent_stock_price,
                                                                          independent_stock_price, pair.hedge_ratio, signal)
                pair.invested_capital = investment_sum
                uninvested_capital -= investment_sum
                backtesting.loc[i, 'Entries'] += 1
                backtesting.loc[i, 'Exits'] += 1
            """
            
        backtesting.loc[i, 'Capital'] = uninvested_capital + sum(pair.invested_capital for pair in pairs)

    return backtesting

def get_sharpe_ratio(capital_series: pd.Series) -> float:
    returns = capital_series.pct_change().dropna()
    valid_returns = returns[(capital_series.shift(1) > 0) & (capital_series > 0)]
    daily_risk_free_rate = RISK_FREE_RATE / ANNUAL_TRADING_DAYS
    excess_returns = valid_returns - daily_risk_free_rate
    mean_return = excess_returns.mean()
    stdev_return = excess_returns.std()

    if stdev_return == 0:
        if mean_return > 0:
            return float('inf')
        elif mean_return == 0:
            return 0.0
        else:
            return float('-inf')

    sharpe_ratio = (ANNUAL_TRADING_DAYS ** 0.5) * mean_return / stdev_return

    return sharpe_ratio

def get_roi(ending_capital: float) -> float:
    return (ending_capital - STARTING_CAPITAL) / STARTING_CAPITAL * 100