# pairs-trading-strategy
## Description

Pairs trading is a mean-reversion investment technique that seeks to exploit the predictable nature of
securities that are closely related. To do this, we specifically look for pairs of securities that
have both of the following properties:

- Correlation
- Cointegration

To measure correlation, we apply Pearson's correlation coefficient to both securities and look for
security pairs that return a coefficient sufficiently close to 1. Cointegration is a slightly more
complex property: two securities with prices X and Y are cointegrated if there is some constant β such
that the spread is a stationary time series, where the spread is equal to X - (β * Y). We identify
cointegrated pairs with the Engle-Granger method, and verify the stationarity of the spread with the
Augmented Dickey-Fuller test. The constant β is referred to as the hedge ratio.

Once we have identified a cointegrated pair, we note that the spread is stationary and thus has a
constant mean. Hence, we keep note of any particularly large deviations from this mean (generally by
tracking the Z-score of the spread) and invest with the expectation that the spread will revert back
to its mean. Naturally, we short the spread when its price is sufficiently greater than the mean, and
we symmetrically enter a long position when it is less than the mean.

Due to the fact that this technique has a relatively simple methodology (and generates trading signals
without too much computation), we can implement backtesting extremely easily. This demonstrates how
the trading strategy would have performed if it were in use over the past few years.

![Graphs of pairs trading results using Ford and General Motors stocks](/example_graphs.png)