from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI
from surmount.logging import log
import json

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
        Execute the trading strategy for SPY based on MACDs value.

        :param data: The market data provided by the Surmount trading environment.
        :return: A TargetAllocation object defining the target allocations for the assets.
        """
        # Initialize allocation to the current holdings or default to 0
        holdings = data["holdings"]
        allocation = holdings.get("SPY", 0)

        # Compute the MACD for SPY. Here we're using a standard fast=12, slow=26 period configuration.
        macd_result = MACD("SPY", data["ohlcv"], 12, 26)
        rsi_value = RSI("SPY", data, 14)

        r = json.dumps(rsi_value)
        log(r)


        if macd_result:
            # Extract the Signal line (MACDs) from the returned dictionary
            signal_line = macd_result.get("MACDs_12_26_9", [])

            # Ensure sufficient data is available for processing
            if len(signal_line) > 1:
                current_macds = signal_line[-1]  # Get the most recent MACDs value

                # Debug the current indicator value
                log(f"MACDs Signal: {current_macds}")
                log(f"RSI Signal: {rsi_value}")

                # Allocation logic based on MACDs value
                if current_macds < -0.45 and rsi_value < 45:
                    allocation = 1.0  # Full allocation to SPY
                    log("MACDs < -0.45 and RSI < 45: Allocating 100% to SPY.")
                elif current_macds > 0.6 or rsi_value > 60:
                    allocation = 0.2  # Partial allocation to SPY
                    log("MACDs > 0.6 or RSI > 60: Allocating 20% to SPY.")
                else:
                    log("No change in allocation.")

        # Return the allocation advisory for SPY
        return TargetAllocation({"SPY": allocation})
