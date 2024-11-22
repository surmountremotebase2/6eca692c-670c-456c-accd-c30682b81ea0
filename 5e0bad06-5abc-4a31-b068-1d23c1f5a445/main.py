from surmount.technical_indicators import MACD
from surmount.base_class import Strategy

class MACDTradingStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY"]  # Trade only SPY

    @property
    def interval(self):
        return "15min"  # Use 15-minute data

    def on_start(self):
        # Initialize variables and indicators
        self.macd = None
        self.previous_macd_signal = None
        self.logger.info("MACD Trading Strategy Initialized.")

    def run(self, data):
        # Extract required data
        holdings = data["holdings"]
        ohlcv = data["ohlcv"].get("SPY")

        # Ensure data is available
        if not ohlcv:
            self.logger.warning("No OHLCV data for SPY. Skipping.")
            return None

        # Calculate MACD
        macd_values = MACD("SPY", ohlcv, fast=12, slow=26, signal=9)

        # Ensure MACD returns valid values
        if isinstance(macd_values, tuple) and len(macd_values) == 2:
            macd_line, signal_line = macd_values
        else:
            self.logger.warning("Invalid MACD data. Skipping.")
            return None

        # Current MACD and Signal values
        macd_value = macd_line[-1]
        signal_value = signal_line[-1]

        self.logger.info(f"MACD: {macd_value}, Signal: {signal_value}")

        # Determine trade signals
        allocation = {}
        if self.previous_macd_signal is not None:
            if macd_value > signal_value and self.previous_macd_signal <= signal_value:
                # Buy signal: MACD crosses above Signal
                self.logger.info("Buy Signal Detected.")
                allocation["SPY"] = 1.0  # Allocate 100% to SPY

            elif macd_value < signal_value and self.previous_macd_signal >= signal_value:
                # Sell signal: MACD crosses below Signal
                self.logger.info("Sell Signal Detected.")
                allocation["SPY"] = 0.0  # Sell all SPY holdings

        # Update the previous MACD signal value
        self.previous_macd_signal = signal_value

        # Return the target allocation
        return allocation if allocation else None
