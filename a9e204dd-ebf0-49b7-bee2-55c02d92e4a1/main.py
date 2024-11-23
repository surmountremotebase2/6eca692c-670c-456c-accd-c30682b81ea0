from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI
from surmount.logging import log

class MACDCrossoverStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY", "SQQQ"]  # Include both SPY and SQQQ

    @property
    def interval(self):
        return "5min"

    def run(self, data):
        """
        Execute the trading strategy for SPY and SQQQ based on MACD bullish and bearish signals.

        :param data: Market data provided by the Surmount trading environment.
        :return: TargetAllocation with updated asset allocations.
        """
        # Ensure allocation is always a dictionary
        holdings = data["holdings"]
        allocation = {"SPY": holdings.get("SPY", 0), "SQQQ": holdings.get("SQQQ", 0)}

        # Calculate MACD and RSI
        try:
            macd_result = MACD("SPY", data["ohlcv"], 12, 26)
            signal_line = macd_result.get("MACDs_12_26_9", [])
            macd_line = macd_result.get("MACD_12_26_9", [])
            rsi_values = RSI("SPY", data, 14)
            rsi_value = rsi_values[-1] if rsi_values else 50  # Default to neutral RSI
        except Exception as e:
            log(f"Error calculating indicators: {e}")
            return None

        # Validate MACD result
        if len(signal_line) > 1 and len(macd_line) > 1:
            # Calculate current and previous differences
            current_diff = macd_line[-1] - signal_line[-1]
            previous_diff = macd_line[-2] - signal_line[-2]

            # Check for bearish convergence
            if current_diff > 0 and previous_diff > current_diff:
                log("Bearish convergence detected: MACD is moving closer to Signal Line.")
                allocation["SQQQ"] = 0.5  # Allocate 50% to SQQQ
                allocation["SPY"] = 0.0  # Exit SPY

            # Check for bullish crossover
            elif macd_line[-2] < signal_line[-2] and macd_line[-1] > signal_line[-1]:
                log("Bullish crossover detected: MACD Line has crossed above Signal Line.")
                allocation["SPY"] = 1.0  # Allocate 100% to SPY
                allocation["SQQQ"] = 0.0  # Exit SQQQ

            # No actionable signal
            else:
                log("No actionable signals. Maintaining current allocation.")

        # Return the target allocation
        return TargetAllocation(allocation)
