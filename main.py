from fetch_data import get_cointegrated_pairs, get_correlated_pairs, get_hedge_ratios, get_market_data, get_returns

def main():
    tickers = ['AAPL', 'AZN', 'BARC.L', 'BP.L', 'F', 'GM', 'GSK',
               'KO', 'LLOY.L', 'MSFT', 'PEP', 'SHEL.L', 'TGT', 'WMT']

    market_data = get_market_data(tickers)
    market_returns = get_returns(market_data)
    correlated_pairs = get_correlated_pairs(market_returns)
    cointegrated_pairs = get_cointegrated_pairs(correlated_pairs, market_data)
    for cointegrated_pair in cointegrated_pairs:
        hedge_ratios = get_hedge_ratios(cointegrated_pair[1])
        print(f"{cointegrated_pair[0]} has hedge ratios {hedge_ratios[0]} and {hedge_ratios[1]}.")
        # spread1 = stock1 - hedge_ratios[0] * stock2
        # spread2 = stock2 - hedge_ratios[1] * stock1
        # ...run ADF on both, select spread with better p_value

if __name__ == '__main__':
    main()
