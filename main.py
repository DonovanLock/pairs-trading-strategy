import sys
from backtesting import get_roi, get_sharpe_ratio, perform_backtest
from fetch_data import get_best_spread, get_cointegrated_pairs, get_correlated_pairs, get_hedge_ratios, get_market_data, get_returns, get_z_score
from graph_data import graph_backtesting, graph_pair_trade
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
    
    backtesting_results = perform_backtest(selected_pairs)
    roi = get_roi(backtesting_results['Capital'].iloc[-1])
    sharpe_ratio = get_sharpe_ratio(backtesting_results['Capital'])
    print(f'Final ROI: {roi:.2f}%, Sharpe Ratio: {sharpe_ratio:.3f}\n')
    graph_backtesting(backtesting_results)

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
