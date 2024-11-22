from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    # Define the assets this strategy will trade
    @property
    def assets(self):
        return ["SPY"]

    # Set the interval for the data. This strategy uses 5-minute intervals.
    @property
    def interval(self):
        return "5min"

    def run(self, data):
        """
        Execute the trading strategy for SPY based on MACD signal.

        :param data: The market data provided by the Surmount trading environment.
        :return: A TargetAllocation object defining the target allocations for the assets.
        """
        # Initialize allocation to 0 implying no position
        allocation = 0

        # Compute the MACD for SPY. Here we're using a standard fast=12, slow=26 period configuration.
        macd_result = MACD("SPY", data["ohlcv"], 12, 26)

        if macd_result is not None:
            # Extract the MACD line, Signal line, and Histogram
            macd_line = macd_result["macd"]
            signal_line = macd_result["signal"]
            histogram = macd_result["histogram"]

            # Ensure we have at least one period worth of data
            if len(histogram) > 1:
                # Trading signal based on MACD strategy:
                # If the MACD line crosses above the signal line, we consider this a buy signal
                # If the MACD line crosses below the signal line, we consider this a sell signal

                # Check for a buy signal
                if histogram[-2] < 0 and histogram[-1] > 0:
                    allocation = 1  # Full allocation to SPY
                    log("MACD bullish crossover. Going long on SPY.")
                # Check for a sell signal
                elif histogram[-2] > 0 and histogram[-1] < 0:
                    allocation = 0  # Move to cash (No position)
                    log("MACD bearish crossover. Exiting position in SPY.")

        # Return the allocation advisory for SPY
        return TargetAllocation({"SPY": allocation})