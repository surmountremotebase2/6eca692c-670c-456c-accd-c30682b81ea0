
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY", "QQQ", "VTI", "VXUS"]

    @property
    def interval(self):
        return "5min"  # Primary interval; we will handle others manually

    def run(self, data):
        total_rsi = {ticker: 0 for ticker in self.assets}
        bullish_macd_count = {ticker: 0 for ticker in self.assets}
        allocations = {}

        for ticker in self.assets:
            ohlcv_data = data['ohlcv'][ticker]
            rsi_value = RSI(ticker, ohlcv_data, 14)
            macd_indicator = MACD(ticker, ohlcv_data, 12, 26)
            macd_line = macd_indicator['MACD']
            signal_line = macd_indicator['signal']

            # Check latest MACD line vs Signal line for bullish signal
            if macd_line[-1] > signal_line[-1]:
                bullish_macd_count[ticker] += 1

            # Accumulate RSI for average calculation
            total_rsi[ticker] += rsi_value[-1]

        # Determine allocations based on RSI and bullish MACD signals
        total_weight = 0
        for ticker in self.assets:
            avg_rsi = total_rsi[ticker]
            if avg_rsi > 50 and bullish_macd_count[ticker] >= 2:
                allocations[ticker] = avg_rsi
                total_weight += avg_rsi
            else:
                allocations[ticker] = 0  # Or set a smaller allocation as per the strategy rules

        # Normalizing allocations to make the sum between 0 and 1
        for ticker in allocations:
            if total_weight > 0:
                allocations[ticker] /= total_weight
            else:
                allocations[ticker] = 1 / len(self.assets)  # Even distribution if total_weight is 0

        return TargetAllocation(allocations)
