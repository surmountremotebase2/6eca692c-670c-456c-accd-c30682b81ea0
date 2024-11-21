from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Configure the ticker for the asset we are interested in trading.
        self.ticker = "AAPL"

    @property
    def assets(self):
        # The assets this strategy will request data for and potentially trade.
        return [self.ticker]

    @property
    def interval(self):
        # Set the interval for data collection. "1day" for daily RSI calculation.
        return "1day"

    def run(self, data):
        # Implement the strategy logic to determine buy or sell signals based on RSI.
        
        # Check if we have enough data to calculate RSI.
        if len(data["ohlcv"]) >= 14:  # Assuming we need at least 14 data points for RSI calculation.
            # Calculate the RSI for the ticker.
            rsi_values = RSI(self.ticker, data["ohlcv"], 14)
            
            if rsi_values is not None:
                current_rsi = rsi_values[-1]  # Get the latest RSI value.
                
                # Decide on the action based on RSI value.
                if current_rsi < 30:
                    # If RSI is below 30, buy signal, allocate 100% to this ticker.
                    allocation = {self.ticker: 1.0}
                elif current_rsi > 70:
                    # If RSI is above 70, sell signal, allocate 0% to this ticker.
                    allocation = {self.ticker: 0}
                else:
                    # If RSI is between 30 and 70, hold, keep previous allocation.
                    # You may need to implement logic to maintain the previous state or decide a default action here.
                    allocation = {self.ticker: 0.5}  # This is an example and might need adjustment based on actual needs.
            else:
                # In case RSI values cannot be calculated, decide on a default action.
                allocation = {self.ticker: 0.5}  # This is a placeholder for a neutral stance.
        else:
            # Not enough data to calculate RSI, decide on a default action.
            allocation = {self.ticker: 0.5}  # Placeholder for a neutral stance.
        
        # Log the decision for debugging purposes.
        log(f"Allocation for {self.ticker}: {allocation[self.ticker]} based on RSI")
        
        # Return the target allocation.
        return TargetAllocation(allocation)