import sys
from backtesting import test
from fetch_data import get_best_spread, get_cointegrated_pairs, get_correlated_pairs, get_hedge_ratios, get_market_data, get_returns, get_z_score
from graph_data import graph_pair_trades
from tickers import TICKERS
from trading_signals import get_positions, get_signals

#after implementing backtesting:
#tune several parameters and gauge sharpe ratio to select best combination

def main():
    market_data = get_market_data(TICKERS)
    market_returns = get_returns(market_data)
    correlated_pairs = get_correlated_pairs(market_returns) # this ensures all hedge ratios are positive
    cointegrated_pairs_data = get_cointegrated_pairs(correlated_pairs, market_data)
    selected_pairs = []

    for [[stock1, stock2], pair_data] in cointegrated_pairs_data:
        hedge_ratios = get_hedge_ratios(pair_data[stock1], pair_data[stock2])
        pair_data['Spread'], best_p_value, best_hedge_ratio, dependent_stock, independent_stock = get_best_spread(stock1, stock2, pair_data, hedge_ratios)
        if best_p_value <= 0.05:
            selected_pairs.append(Pair(pair_data, dependent_stock, independent_stock, best_hedge_ratio))
    
    if not selected_pairs:
        sys.exit('No stationary spreads found.')

    for pair in selected_pairs:
        pair.data['Z-score'] = get_z_score(pair.data['Spread'])
        pair.data['Position'] = get_positions(pair.data['Z-score'].dropna())
        pair.data['Signal'] = get_signals(pair.data['Position'])
    
    capital = test(selected_pairs)
    print(capital)
    """
        continue # not stationary

    print(f'Spread = {dependent_stock} - β * {independent_stock}, β = {best_hedge_ratio:.4f}')
    pair_data['Z-score'] = get_z_score(pair_data['Spread'])
    pair_data['Position'] = get_positions(pair_data['Z-score'].dropna())
    pair_data['Signal'] = get_signals(pair_data['Position'])
    pair_data['Capital'], pair_data['Invested'] = get_capital(pair_data[dependent_stock], pair_data[independent_stock],
                                        pair_data['Position'], pair_data['Signal'], best_hedge_ratio)
    
    sharpe_ratio = get_sharpe_ratio(pair_data['Invested'])
    roi = get_roi(pair_data['Capital'].iloc[-1])
    
    print(f'ROI: {roi:.2f}%, Sharpe Ratio: {sharpe_ratio:.4f}\n')
    graph_pair_trades(stock1, stock2, pair_data)
    """

class Pair:
    def __init__(self, data, dependent_stock, independent_stock, hedge_ratio):
        self.data = data
        self.dependent_stock = dependent_stock
        self.independent_stock = independent_stock
        self.hedge_ratio = hedge_ratio
        self.invested_capital = 0
        self.long_shares = 0
        self.short_shares = 0
        self.short_entry_price = 0

if __name__ == '__main__':
    main()
