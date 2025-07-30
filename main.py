from fetch_data import get_best_spread, get_cointegrated_pairs, get_correlated_pairs, get_hedge_ratios, get_market_data, get_returns
import matplotlib.pyplot as plt

def main():
    tickers = ['AAPL', 'AZN', 'BARC.L', 'BP.L', 'F', 'GM', 'GSK',
               'KO', 'LLOY.L', 'MSFT', 'PEP', 'SHEL.L', 'TGT', 'WMT']

    market_data = get_market_data(tickers)
    market_returns = get_returns(market_data)
    correlated_pairs = get_correlated_pairs(market_returns)
    cointegrated_pairs = get_cointegrated_pairs(correlated_pairs, market_data)

    for cointegrated_pair in cointegrated_pairs:
        hedge_ratios = get_hedge_ratios(cointegrated_pair[1])
        
        best_spread, best_p_value, best_hedge_ratio, dependent_stock, independent_stock = get_best_spread(cointegrated_pair, hedge_ratios)
        if best_p_value > 0.05:
            continue # not stationary

        print(f'Using {dependent_stock} - {best_hedge_ratio} * {independent_stock} as a stationary spread')
        plt.plot(best_spread.index, best_spread.values, label='Spread')
        plt.show()
        
        

if __name__ == '__main__':
    main()
