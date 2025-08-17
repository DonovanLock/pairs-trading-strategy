import sys
import pandas as pd

from config import ANNUAL_TRADING_DAYS, PORTFOLIO_PORTION_INVESTED_PER_TRADE, RISK_FREE_RATE, STARTING_CAPITAL
from trading_signals import Position, Signal

#reminder: dependent stock - hedge ratio * independent stock = stationary spread
#z_score < -ENTRY_THRESHOLD -> go long on spread -> buy dependent stock, sell independent stock
#z_score > ENTRY_THRESHOLD -> go short on spread -> sell dependent stock, buy independent stock

def get_invested_capital(long_stock, short_stock, long_shares,
                         short_shares, short_entry_price):
    long_market_value = long_stock * long_shares
    short_market_value = ((2 * short_entry_price) - short_stock) * short_shares
    return long_market_value + short_market_value

def enter_position(investment_sum, dependent_stock,
                   independent_stock, hedge_ratio, signal):
    if signal == Signal.ENTER_LONG or signal == Signal.EXIT_SHORT_AND_ENTER_LONG:
        long_shares = investment_sum / (dependent_stock + hedge_ratio * independent_stock)
        short_shares = hedge_ratio * long_shares
        short_entry_price = independent_stock
    elif signal == Signal.ENTER_SHORT or signal == Signal.EXIT_LONG_AND_ENTER_SHORT:
        short_shares = investment_sum / (dependent_stock + hedge_ratio * independent_stock)
        long_shares = hedge_ratio * short_shares
        short_entry_price = dependent_stock
    return long_shares, short_shares, short_entry_price

def perform_backtest(pairs):
    indexCheck = all(pair.data['Signal'].index.equals(pairs[0].data['Signal'].index) for pair in pairs[1:])
    if not indexCheck:
        sys.exit('All spreads must have the same index for backtesting.') #this should never happen
    
    for pair in pairs:
        pair.data['Invested'] = pd.Series(index=pair.data['Signal'].dropna().index, data=0)

    capital = pd.Series(index=pairs[0].data['Signal'].dropna().index)
    uninvested_capital = STARTING_CAPITAL
    for i in capital.index:
        # update invested capital for each pair
        # calculate total capital
        for pair in pairs:
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
            
            elif signal == Signal.ENTER_SHORT:
                investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * uninvested_capital
                pair.long_shares, pair.short_shares, pair.short_entry_price = enter_position(investment_sum, dependent_stock_price,
                                                                          independent_stock_price, pair.hedge_ratio, signal)
                pair.invested_capital = investment_sum
                uninvested_capital -= investment_sum
            
            elif signal == Signal.EXIT_LONG:
                pair.invested_capital = get_invested_capital(dependent_stock_price,
                                                             independent_stock_price,
                                                             pair.long_shares, pair.short_shares,
                                                             pair.short_entry_price)
                uninvested_capital += pair.invested_capital
                pair.invested_capital = pair.long_shares = pair.short_shares = pair.short_entry_price = 0
                
            elif signal == Signal.EXIT_SHORT:
                pair.invested_capital = get_invested_capital(independent_stock_price,
                                                             dependent_stock_price,
                                                             pair.long_shares, pair.short_shares,
                                                             pair.short_entry_price)
                uninvested_capital += pair.invested_capital
                pair.invested_capital = pair.long_shares = pair.short_shares = pair.short_entry_price = 0
            
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

        capital[i] = uninvested_capital + sum(pair.invested_capital for pair in pairs)
    
    return capital

def get_sharpe_ratio(capital_series):
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

def get_roi(ending_capital):
    return (ending_capital - STARTING_CAPITAL) / STARTING_CAPITAL * 100