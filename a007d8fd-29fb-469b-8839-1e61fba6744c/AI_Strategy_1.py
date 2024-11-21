from surmount.technical_indicators import MACD, RSI
from surmount.base_class import Strategy, TargetAllocation

class IntradayTradingStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY", "QQQ", "VTI", "VXUS"]

    @property
    def interval(self):
        return "5min"

    def run(self, data):
        holdings = data["holdings"]
        ohlcv_data = data["ohlcv"]

        intervals = ["5min", "10min", "15min"]
        allocation_dict = {}
        rsi_signals = {ticker: [] for ticker in self.assets}
        macd_signals = {ticker: [] for ticker in self.assets}

        for ticker in self.assets:
            for interval in intervals:
                try:
                    # Fetch interval-specific data
                    ohlcv = self.get_ohlcv(ticker, interval)

                    # Calculate RSI
                    rsi = RSI(ticker, ohlcv, 14)
                    rsi_value = rsi[-1] if rsi else 50  # Fallback to neutral RSI if data missing

                    # Calculate MACD
                    macd_values = MACD(ticker, ohlcv, fast=12, slow=26, signal=9)

                    # Ensure MACD returns valid structure
                    if isinstance(macd_values, tuple) and len(macd_values) == 2:
                        macd_line, signal_line = macd_values
                        rsi_signals[ticker].append(rsi_value)
                        macd_signals[ticker].append(macd_line[-1] > signal_line[-1])  # True if MACD > Signal
                    else:
                        raise ValueError("Invalid MACD return structure")

                except Exception as e:
                    # Log error for debugging and set fallback values
                    self.logger.warning(f"Error processing {ticker} at {interval}: {e}")
                    rsi_signals[ticker].append(50)  # Neutral RSI
                    macd_signals[ticker].append(False)  # No bullish confirmation

        # Consolidate signals across intervals
        for ticker in self.assets:
            # Average RSI across intervals
            avg_rsi = sum(rsi_signals[ticker]) / len(rsi_signals[ticker])

            # Check if MACD is bullish in at least two intervals
            macd_bullish_count = sum(macd_signals[ticker])
            macd_confirmed = macd_bullish_count >= 2

            # Allocation logic
            if macd_confirmed:
                allocation_dict[ticker] = avg_rsi / sum(
                    sum(rsi_signals[t]) / len(rsi_signals[t]) for t in self.assets
                )

        # Rebalance only if deviation exceeds 2%
        for key in allocation_dict:
            current_allocation = holdings.get(key, 0)
            target_allocation = allocation_dict[key]
            if abs(target_allocation - current_allocation) > 0.02:
                if target_allocation > current_allocation:
                    self.logger.info(f"BUY {key}: Increase allocation from {current_allocation:.2%} to {target_allocation:.2%}")
                else:
                    self.logger.info(f"SELL {key}: Decrease allocation from {current_allocation:.2%} to {target_allocation:.2%}")
                return TargetAllocation(allocation_dict)

        return None

    def get_ohlcv(self, ticker, interval):
        """Fetch OHLCV data for a specific ticker and interval."""
        # Placeholder for data-fetching logic
        return self.fetch_data(ticker, interval)
