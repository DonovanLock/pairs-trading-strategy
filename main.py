from backtesting import get_roi, get_sharpe_ratio, perform_backtest
from fetch_data import get_market_data, get_returns
from graph_data import graph_backtesting
from trading_signals import get_positions, get_signals
from validate_pairs import get_cointegrated_pairs, get_correlated_pairs, get_selected_pairs, get_z_score

#after implementing backtesting:
#tune several parameters and gauge sharpe ratio to select best combination

def main() -> None:
    market_data = get_market_data()
    market_returns = get_returns(market_data)
    correlated_pairs = get_correlated_pairs(market_returns) # this ensures all hedge ratios are positive
    cointegrated_pairs_data = get_cointegrated_pairs(correlated_pairs, market_data)
    selected_pairs = get_selected_pairs(cointegrated_pairs_data)

    for pair in selected_pairs:
        #each pair contains pair_data, which tracks the spread of the two stocks from 3-6 years ago.
        #for backtesting, we know want to implement the strategy on the most recent 3 years of data.
        #we use the same spread/hedge ratio. simply update pair.data['Spread'].
        pair.data['Z-score'] = get_z_score(pair.data['Spread'])
        pair.data['Position'] = get_positions(pair.data['Z-score'].dropna())
        pair.data['Signal'] = get_signals(pair.data['Position'])
        print(f'Selected pair: {pair.dependent_stock} and {pair.independent_stock}')

    backtesting_results = perform_backtest(selected_pairs)
    roi = get_roi(backtesting_results['Capital'].iloc[-1])
    sharpe_ratio = get_sharpe_ratio(backtesting_results['Capital'])
    print(f'\nFinal ROI: {roi:.2f}%, Sharpe Ratio: {sharpe_ratio:.3f}\n')

    graph_backtesting(backtesting_results)

if __name__ == '__main__':
    main()
