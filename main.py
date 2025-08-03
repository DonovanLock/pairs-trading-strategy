from fetch_data import ROLLING_WINDOW, get_best_spread, get_cointegrated_pairs, get_correlated_pairs, get_hedge_ratios, get_market_data, get_returns, get_z_score
from graph_data import graph_pair_trades
from trading_signals import get_positions, get_signals

#after implementing backtesting:
#tune several parameters and gauge sharpe ratio to select best combination
#parameters to tune:
#ENTRY_THRESHOLD, ROLLING_WINDOW, NOTIONAL_VALUE_PROPORTION_PER_LEG

def main():
    tickers = ['AAPL', 'AZN', 'BARC.L', 'BP.L', 'F', 'GM', 'GSK',
               'KO', 'LLOY.L', 'MSFT', 'PEP', 'SHEL.L', 'TGT', 'WMT']

    market_data = get_market_data(tickers)
    market_returns = get_returns(market_data)
    correlated_pairs = get_correlated_pairs(market_returns)
    cointegrated_pairs_data = get_cointegrated_pairs(correlated_pairs, market_data)

    for [[stock1, stock2], pair_data] in cointegrated_pairs_data:
        hedge_ratios = get_hedge_ratios(pair_data[stock1], pair_data[stock2])
        pair_data['Spread'], best_p_value, best_hedge_ratio, dependent_stock, independent_stock = get_best_spread(stock1, stock2, pair_data, hedge_ratios)

        if best_p_value > 0.05:
            continue # not stationary

        print(f'Using {dependent_stock} - {best_hedge_ratio} * {independent_stock} as a stationary spread')
        pair_data['Z-score'] = get_z_score(pair_data['Spread'])
        pair_data['Position'] = get_positions(pair_data['Z-score'].dropna())
        pair_data['Signal'] = get_signals(pair_data['Position'])

        print(pair_data.iloc[ROLLING_WINDOW-1:].head(60))
        graph_pair_trades(stock1, stock2, pair_data)

if __name__ == '__main__':
    main()
