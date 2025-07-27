import yfinance as yf

data = yf.download(['AAPL', 'NVDA'], period='3y', auto_adjust=False)
#for this to work with a vpn, i need to switch country every time it runs?
if 'Adj Close' in data.columns:
    adj_data = data['Adj Close']
else:
    adj_data = data['Close']
print(adj_data)