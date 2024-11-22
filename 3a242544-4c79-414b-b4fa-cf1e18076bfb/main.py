import json
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
        log("ruvt11")

        if macd_result:
            # Extract the MACD line, Signal line, and Histogram from the returned dictionary
            macd_line = macd_result.get("MACD_12_26_9", [])
            signal_line = macd_result.get("MACDs_12_26_9", [])
            histogram = macd_result.get("MACDh_12_26_9", [])

            # Ensure sufficient data is available for processing
            if len(macd_line) > 1 and len(signal_line) > 1 and len(histogram) > 1:
                # Debug the current indicator values
                log.info(f"MACD Line: {macd_line[-1]}, Signal Line: {signal_line[-1]}, Histogram: {histogram[-1]}")

                # Check for a bullish crossover (Buy signal)
                if histogram[-2] < 0 and histogram[-1] > 0:
                    allocation = 1  # Full allocation to SPY
                    log.info("MACD bullish crossover. Going long on SPY.")
                # Check for a bearish crossover (Sell signal)
                elif histogram[-2] > 0 and histogram[-1] < 0:
                    allocation = 0  # Move to cash (No position)
                    log.info("MACD bearish crossover. Exiting position in SPY.")

        # Return the allocation advisory for SPY
        return TargetAllocation({"SPY": allocation})
