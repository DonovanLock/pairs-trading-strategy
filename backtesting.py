import pandas as pd

from config import PORTFOLIO_PORTION_INVESTED_PER_TRADE, STARTING_CAPITAL
from trading_signals import Position, Signal

#reminder: dependent stock - hedge ratio * independent stock = stationary spread
#z_score < -ENTRY_THRESHOLD -> go long on spread -> buy dependent stock, sell independent stock
#z_score > ENTRY_THRESHOLD -> go short on spread -> sell dependent stock, buy independent stock

def get_invested_capital(long_stock, short_stock, long_shares,
                         short_shares, short_entry_price):
    long_market_value = long_stock * long_shares
    short_market_value = ((2 * short_entry_price) - short_stock) * short_shares
    return long_market_value + short_market_value

def update_capital(idle_capital, long_stock, short_stock,
                   long_shares, short_shares, short_entry_price):
    return idle_capital + get_invested_capital(long_stock, short_stock, long_shares,
                                               short_shares, short_entry_price)

def reset_to_flat_position(current_capital):
    return 0, 0, 0, current_capital

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


def get_capital(dependent_stock, independent_stock,
                positions, signals, hedge_ratio):
    signal_entries = signals.dropna()
    capital = pd.Series(index=signal_entries.index)
    current_capital = STARTING_CAPITAL # current_capital = idle_capital + long_market_value + short_market_value
    long_shares, short_shares, short_entry_price, idle_capital = reset_to_flat_position(current_capital)

    for i in signal_entries.index:
        position = Position[positions[i]]
        signal = Signal[signals[i]]

        if signal == Signal.NONE:
            if position == Position.LONG:
                #update current_capital
                current_capital = update_capital(idle_capital, dependent_stock[i], independent_stock[i],
                                                 long_shares, short_shares, short_entry_price)
            elif position == Position.SHORT:
                #update current_capital
                current_capital = update_capital(idle_capital, independent_stock[i], dependent_stock[i],
                                                 long_shares, short_shares, short_entry_price)
        elif signal == Signal.ENTER_LONG:
            #enter long
            investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * current_capital
            long_shares, short_shares, short_entry_price = enter_position(investment_sum, dependent_stock[i],
                                                                          independent_stock[i], hedge_ratio, signal)
            idle_capital = current_capital - get_invested_capital(dependent_stock[i], independent_stock[i],
                                                                  long_shares, short_shares, short_entry_price)
        elif signal == Signal.ENTER_SHORT:
            #enter short
            investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * current_capital
            long_shares, short_shares, short_entry_price = enter_position(investment_sum, dependent_stock[i],
                                                                          independent_stock[i], hedge_ratio, signal)
            idle_capital = current_capital - get_invested_capital(independent_stock[i], dependent_stock[i],
                                                                  long_shares, short_shares, short_entry_price)
        elif signal == Signal.EXIT_LONG:
            #update current_capital and exit long
            current_capital = update_capital(idle_capital, dependent_stock[i], independent_stock[i],
                                             long_shares, short_shares, short_entry_price)
            long_shares = short_shares = short_entry_price = 0
            idle_capital = current_capital
        elif signal == Signal.EXIT_SHORT:
            #update current_capital and exit short
            current_capital = update_capital(idle_capital, independent_stock[i], dependent_stock[i],
                                             long_shares, short_shares, short_entry_price)
            long_shares, short_shares, short_entry_price, idle_capital = reset_to_flat_position(current_capital)
        elif signal == Signal.EXIT_LONG_AND_ENTER_SHORT:
            #update current_capital and exit long
            #enter short
            current_capital = update_capital(idle_capital, dependent_stock[i], independent_stock[i],
                                             long_shares, short_shares, short_entry_price)
            investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * current_capital
            long_shares, short_shares, short_entry_price = enter_position(investment_sum, dependent_stock[i],
                                                                          independent_stock[i], hedge_ratio, signal)
            idle_capital = current_capital - get_invested_capital(independent_stock[i], dependent_stock[i],
                                                                  long_shares, short_shares, short_entry_price)
        else:
            #update current_capital and exit short
            #enter long
            current_capital = update_capital(idle_capital, independent_stock[i], dependent_stock[i],
                                             long_shares, short_shares, short_entry_price)
            investment_sum = PORTFOLIO_PORTION_INVESTED_PER_TRADE * current_capital
            long_shares, short_shares, short_entry_price = enter_position(investment_sum, dependent_stock[i],
                                                                          independent_stock[i], hedge_ratio, signal)
            idle_capital = current_capital - get_invested_capital(dependent_stock[i], independent_stock[i],
                                                                  long_shares, short_shares, short_entry_price)
        
        capital[i] = current_capital
    
    return capital