from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI
from surmount.logging import log

class TradingStrategy(Strategy):
    # Define the assets this strategy will trade
    @property
    def assets(self):
        return ["SPY", "SQQQ"]

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
        sq_allocation = holdings.get("SQQQ", 0)

        # Compute the MACD for SPY. Here we're using a standard fast=12, slow=26 period configuration.
        macd_result = MACD("SPY", data["ohlcv"], 12, 26)
        rsi_result = RSI("SPY", data, 14)

        if macd_result:
            # Extract the Signal line (MACDs) from the returned dictionary
            signal_line = macd_result.get("MACDs_12_26_9", [])
            macd_line = macd_result.get("MACD_12_26_9", [])

            rsi_data = rsi_result[-3:]
        
    
            slope_1 = (rsi_data[1] - rsi_data[0]) / 1
            slope_2 = (rsi_data[2] - rsi_data[1]) / 1
            
            rsi_slope =  (slope_1 + slope_2) / 2
            
            current_diff = macd_line[-1] - signal_line[-1]
            previous_diff = macd_line[-2] - signal_line[-2]
            
            if rsi_slope < -3:
                allocation = 1.0
                sq_allocation = 0.0
            elif macd_line[-2] < signal_line[-2] and macd_line[-1] > signal_line[-1]:
                log("Bullish crossover detected: MACD Line has crossed above Signal Line.")
                allocation = 1.0  # Allocate 100% to SPY
                sq_allocation = 0.0
                
            # Check for bearish convergence
            if current_diff > 0 and previous_diff > current_diff:
                log("Bearish convergence detected: MACD is moving closer to Signal Line.")
                allocation = 0.0  # Reduce exposure to SPY
                sq_allocation = 0.5
           

        return TargetAllocation({"SPY": allocation, "SQQQ": sq_allocation})
