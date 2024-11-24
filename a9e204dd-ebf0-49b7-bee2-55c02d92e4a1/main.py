from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI, EMA
from surmount.logging import log

class LongHoldingTradingStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY"]

    @property
    def interval(self):
        return "5min"

    def on_start(self):
        # Track holding periods and last allocation
        self.holding_period = 0
        self.last_allocation = 0.0

    def run(self, data):
        """
        Execute the trading strategy for SPY with a holding period.

        :param data: Market data provided by the Surmount trading environment.
        :return: TargetAllocation with updated asset allocations.
        """
        holdings = data["holdings"]
        allocation = holdings.get("SPY", 0)

        # Compute indicators
        macd_result = MACD("SPY", data["ohlcv"], 12, 26)
        rsi_result = RSI("SPY", data, 14)
        ema_50 = EMA("SPY", data["ohlcv"], 50)[-1] if EMA("SPY", data["ohlcv"], 50) else None
        current_price = data["ohlcv"]["SPY"]["close"]

        if macd_result and rsi_result and ema_50:
            # Extract MACD and Signal Line
            signal_line = macd_result.get("MACDs_12_26_9", [])
            macd_line = macd_result.get("MACD_12_26_9", [])
            rsi_data = rsi_result[-3:]

            # Calculate RSI slope
            rsi_slope = (rsi_data[-1] - rsi_data[0]) / 2

            # Calculate MACD difference
            current_diff = macd_line[-1] - signal_line[-1]
            previous_diff = macd_line[-2] - signal_line[-2]

            # Track holding period
            self.holding_period += 1

            # Trade logic with holding period
            if self.holding_period >= 5:  # Minimum holding period
                # Bullish crossover: MACD crosses above Signal
                if macd_line[-2] < signal_line[-2] and macd_line[-1] > signal_line[-1]:
                    log("Bullish crossover detected: Allocating to SPY.")
                    allocation = 1.0  # Allocate 100% to SPY
                    self.holding_period = 0  # Reset holding period

                # Bearish convergence: MACD moves closer to Signal
                elif current_diff > 0 and previous_diff > current_diff:
                    log("Bearish convergence detected: Reducing SPY allocation.")
                    allocation = 0.0  # Exit SPY
                    self.holding_period = 0  # Reset holding period

            # If no strong signal, maintain the current allocation
            else:
                log(f"Holding current allocation for {self.holding_period} intervals.")

        # Update the last allocation for debugging and return the target allocation
        self.last_allocation = allocation
        return TargetAllocation({"SPY": allocation})
