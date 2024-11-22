from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "SPY"

    @property
    def assets(self):
        return [self.ticker]

    @property
    def interval(self):
        return "5min"  # Define the interval for the strategy

    def run(self, data):
        # Initialize allocation for SPY
        allocation_dict = {self.ticker: 0.0}

        # Ensure the necessary data is available
        if len(data["ohlcv"]) < 26:  # MACD(12,26) requires at least 26 data points
            return TargetAllocation(allocation_dict)

        # Calculate MACD and RSI for the SPY
        macd_values = MACD(self.ticker, data["ohlcv"], fast=12, slow=26)
        rsi_values = RSI(self.ticker, data["ohlcv"], length=14)

        # Check the latest MACD and RSI values to decide on allocation
        if macd_values["MACD"][-1] < -0.45 and rsi_values[-1] < 40: 
            allocation_dict[self.ticker] = 1.0  # SPY allocation set to 100%
        elif macd_values["MACD"][-1] > 0.75 and rsi_values[-1] > 70:
            allocation_dict[self.ticker] = 0.2  # SPY allocation set to 20%

        return TargetAllocation(allocation_dict)