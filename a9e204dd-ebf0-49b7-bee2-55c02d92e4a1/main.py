from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI, EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY"]

    @property
    def interval(self):
        return "5min"

    def on_start(self):
        """
        Initialize the strategy. This method is called once when the strategy starts.
        """
        self.current_signal = "neutral"  # Track the current signal
        self.holding_period = 0  # Count how long a position is held

    def run(self, data):
        """
        Execute the trading strategy for SPY based on MACD, RSI, and EMA.

        :param data: Market data provided by the Surmount trading environment.
        :return: TargetAllocation with updated asset allocations.
        """
        holdings = data["holdings"]
        allocation = holdings.get("SPY", 0)

        # Compute indicators
        macd_result = MACD("SPY", data["ohlcv"], 12, 26)
        rsi_result = RSI("SPY", data, 14)
        ema_50 = EMA("SPY", data["ohlcv"], 50)[-1] if EMA("SPY", data["ohlcv"], 50) else None
        current_price = data["ohlcv"][-1]["SPY"]["close"]  # Extract current price

        if macd_result and rsi_result and ema_50:
            # Extract MACD and Signal Line
            signal_line = macd_result.get("MACDs_12_26_9", [])
            macd_line = macd_result.get("MACD_12_26_9", [])
            rsi_value = rsi_result[-1]

            # Increment holding period counter
            self.holding_period += 1

            # Check for bullish conditions
            if (
                macd_line[-2] < signal_line[-2] and macd_line[-1] > signal_line[-1]
                and rsi_value < 50 and current_price > ema_50
            ):
                if self.current_signal != "bullish" or self.holding_period >= 10:  # Prevent frequent trades
                    log("Bullish signal detected: Allocating 100% to SPY.")
                    allocation = 1.0
                    self.current_signal = "bullish"
                    self.holding_period = 0

            # Check for bearish conditions
            elif (
                macd_line[-2] > signal_line[-2] and macd_line[-1] < signal_line[-1]
                and rsi_value > 70 and current_price < ema_50
            ):
                if self.current_signal != "bearish" or self.holding_period >= 10:  # Prevent frequent trades
                    log("Bearish signal detected: Exiting SPY.")
                    allocation = 0.0
                    self.current_signal = "bearish"
                    self.holding_period = 0

            # No actionable signal
            else:
                log(f"No strong signal detected: Maintaining current allocation. Holding period: {self.holding_period}")

        return TargetAllocation({"SPY": allocation})
