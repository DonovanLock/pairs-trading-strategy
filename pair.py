import pandas as pd

class Pair:
    def __init__(self, data: pd.DataFrame, dependent_stock: str, independent_stock: str, hedge_ratio: float) -> None:
        self.data = data
        self.dependent_stock = dependent_stock
        self.independent_stock = independent_stock
        self.hedge_ratio = hedge_ratio
        self.invested_capital = 0
        self.long_shares = 0
        self.short_shares = 0
        self.short_entry_price = 0