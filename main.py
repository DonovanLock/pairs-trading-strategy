from fetch_data import get_best_spread, get_cointegrated_pairs, get_correlated_pairs, get_hedge_ratios, get_market_data, get_returns, get_z_score
from graph_data import graph_pair_trades
from utils import get_columns_from_pair_data

#after implementing backtesting:
#tune several parameters and gauge sharpe ratio to select best combination
#parameters to tune:
#ENTRY_THRESHOLD, ROLLING_WINDOW
def main():
    tickers = ['AAPL', 'AZN', 'BARC.L', 'BP.L', 'F', 'GM', 'GSK',
               'KO', 'LLOY.L', 'MSFT', 'PEP', 'SHEL.L', 'TGT', 'WMT']

    market_data = get_market_data(tickers)
    market_returns = get_returns(market_data)
    correlated_pairs = get_correlated_pairs(market_returns)
    cointegrated_pairs_data = get_cointegrated_pairs(correlated_pairs, market_data)

    for [[stock1, stock2], pair_data] in cointegrated_pairs_data:
        stock1_data, stock2_data = get_columns_from_pair_data(pair_data)
        hedge_ratios = get_hedge_ratios(stock1_data, stock2_data)
        
        best_spread, best_p_value, best_hedge_ratio, dependent_stock, independent_stock = get_best_spread(stock1, stock2, stock1_data, stock2_data, hedge_ratios)
        if best_p_value > 0.05:
            continue # not stationary

        print(f'Using {dependent_stock} - {best_hedge_ratio} * {independent_stock} as a stationary spread')

        z_score = get_z_score(best_spread)
        graph_pair_trades(stock1, stock2, stock1_data, stock2_data, z_score)     

if __name__ == '__main__':
    main()
