from fetch_data import get_cointegrated_pairs, get_correlated_pairs, get_market_data, get_returns

def main():
    tickers = ['AAPL', 'AZN', 'BARC.L', 'BP.L', 'F', 'GM', 'GSK',
               'KO', 'LLOY.L', 'MSFT', 'PEP', 'SHEL.L', 'TGT', 'WMT']

    market_data = get_market_data(tickers)
    market_returns = get_returns(market_data)
    correlated_pairs = get_correlated_pairs(market_returns)
    print(correlated_pairs)
    cointegrated_pairs = get_cointegrated_pairs(correlated_pairs, market_data)
    print(cointegrated_pairs)

if __name__ == '__main__':
    main()
