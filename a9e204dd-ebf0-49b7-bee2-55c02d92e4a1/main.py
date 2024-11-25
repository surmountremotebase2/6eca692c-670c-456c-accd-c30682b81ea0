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
        self.holding_period = 0  # Initialize the holding period counter

    def run(self, data):
        """
        Execute the trading strategy for SPY based on MACD, RSI, and EMA.

        :param data: Market data provided by the Surmount trading environment.
        :return: TargetAllocation with updated asset allocations.
        """
        # Ensure attributes are initialized
        if not hasattr(self, "current_signal"):
            self.current_signal = "neutral"
        if not hasattr(self, "holding_period"):
            self.holding_period = 0

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

            # Debugging indicator values
            log(f"Current Price: {current_price}, EMA(50): {ema_50}, RSI: {rsi_value}")
            log(f"MACD: {macd_line[-1]}, Signal Line: {signal_line[-1]}")

            # Increment holding period counter
            self.holding_period += 1

            # Looser conditions for bullish and bearish signals
            bullish_condition = (
                macd_line[-1] > signal_line[-1]  # MACD above Signal
                and rsi_value < 60               # RSI below overbought
                and current_price > ema_50       # Price above EMA(50)
            )
            bearish_condition = (
                macd_line[-1] < signal_line[-1]  # MACD below Signal
                and rsi_value > 40               # RSI above oversold
                and current_price < ema_50       # Price below EMA(50)
            )

            # Check for bullish conditions
            if bullish_condition:
                if self.current_signal != "bullish" or self.holding_period >= 10:
                    log("Bullish signal detected: Allocating 100% to SPY.")
                    allocation = 1.0
                    self.current_signal = "bullish"
                    self.holding_period = 0  # Reset holding period

            # Check for bearish conditions
            elif bearish_condition:
                if self.current_signal != "bearish" or self.holding_period >= 10:
                    log("Bearish signal detected: Exiting SPY.")
                    allocation = 0.0
                    self.current_signal = "bearish"
                    self.holding_period = 0  # Reset holding period

            # No actionable signal
            else:
                log(f"No strong signal detected: Maintaining current allocation. Holding period: {self.holding_period}")

        return TargetAllocation({"SPY": allocation})
