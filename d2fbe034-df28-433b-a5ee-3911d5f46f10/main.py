from surmount.technical_indicators import MACD, RSI
from surmount.base_class import Strategy, TargetAllocation

class TradingStrategy(Strategy):

    @property
    def assets(self):
        return ["SPY", "QQQ", "VTI", "VXUS"]

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        holdings = data["holdings"]
        data = data["ohlcv"]

        allocation_dict = {}
        rsi_dict = {}
        macd_signals = {}

        for ticker in self.assets:
            try:
                # Calculate RSI
                rsi_dict[ticker] = RSI(ticker, data, 14)[-1]

                # Calculate MACD
                macd, signal = MACD(ticker, data, fast=12, slow=26, signal=9)
                macd_signals[ticker] = macd[-1] > signal[-1]  # Bullish if MACD > Signal line
            except:
                rsi_dict[ticker] = 1
                macd_signals[ticker] = False

        # Adjust allocation based on RSI and MACD confirmation
        total_rsi = sum(rsi_dict.values()) + 10
        for ticker in self.assets:
            if macd_signals[ticker]:  # Include only assets with bullish MACD confirmation
                allocation_dict[ticker] = rsi_dict[ticker] / total_rsi

        # Rebalance only if deviation exceeds 2%
        for key in allocation_dict:
            if abs(allocation_dict[key] - holdings.get(key, 0)) > 0.02:
                return TargetAllocation(allocation_dict)
        return None
