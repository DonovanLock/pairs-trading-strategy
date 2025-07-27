from fetch_data import get_correlated_pairs, get_market_data

def main():
    #All of these are aerospace/defence companies listed on the LSE.
    tickers = ['AVON.L', 'BA.L', 'BAB.L', 'CHG.L', 'CHRT.L',
               'MRO.L', 'QQ.L', 'RR.L', 'SNR.L']
    
    market_data = get_market_data(tickers)
    correlated_pairs = get_correlated_pairs(market_data)
    print(str(correlated_pairs))

if __name__ == '__main__':
    main()