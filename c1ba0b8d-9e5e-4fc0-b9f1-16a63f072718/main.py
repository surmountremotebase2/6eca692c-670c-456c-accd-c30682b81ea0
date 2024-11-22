class TradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["AAPL", ...]
        self.data_list = [Ratios(ticker) for ticker in self.tickers]

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list