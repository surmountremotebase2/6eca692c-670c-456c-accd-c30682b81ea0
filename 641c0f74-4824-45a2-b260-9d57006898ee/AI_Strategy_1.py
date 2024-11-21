from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD
from surmount.data import ohlcv
from collections import defaultdict

class TradingStrategy(Strategy):
    def __init__(self):
        self.assets = ["SPY", "QQQ", "VTI", "VXUS"]
        self.intervals = ["5min", "10min", "15min"]

    @property
    def interval(self):
        # This strategy integrates multiple intervals, handle interval dynamically within run() instead
        pass

    def run(self, data):
        rsi_scores = defaultdict(list)
        macd_signals = defaultdict(int)

        for asset in self.assets:
            for interval in self.intervals:
                # Retrieve OHLCV data
                ohlcv_data = ohlcv(asset=asset, interval=interval)

                # Calculate RSI
                rsi = RSI(asset, ohlcv_data, 14)
                rsi_scores[asset].append(rsi[-1])  # Get the latest RSI value
                
                # Calculate MACD and Signal line
                macd_output = MACD(asset, ohlcv_data, fast=12, slow=26, signal=9)
                macd_line = macd_output["MACD"][-1]
                signal_line = macd_output["signal"][-1]

                # Check if MACD is bullish
                if macd_line > signal_line:
                    macd_signals[asset] += 1

        # Calculate target allocations based on signals
        target_allocations = {}
        for asset in self.assets:
            average_rsi = sum(rsi_scores[asset]) / len(rsi_scores[asset])
            bullish_macd_count = macd_signals[asset]
            
            # Determine buy signal based on conditions outlined in steps 4 and 5
            if average_rsi > 50 and bullish_macd_count >= 2:
                # Assign allocation weight relative to its average RSI, normalized by 70 for demonstration
                target_allocations[asset] = min(0.25, average_rsi / 70)  # Example allocation cap at 25%
            else:
                # Assign a lower allocation or remove it from the portfolio
                target_allocations[asset] = 0

        # Normalize allocations to ensure they sum to 1 (or less depending on strategy)
        allocation_sum = sum(target_allocations.values())
        if allocation_sum > 0:
            normalized_allocations = {asset: weight / allocation_sum for asset, weight in target_allocations.items()}
        else:
            normalized_allocations = {asset: 0 for asset in self.assets}

        return TargetAllocation(normalized_allocations)