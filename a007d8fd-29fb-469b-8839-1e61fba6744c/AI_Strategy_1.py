from surmount.base_class import Strategy, TargetAllocation
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker you want to trade
        self.ticker = "SPY"

    @property
    def interval(self):
        # The data interval for trading decisions
        return "1day"

    @property
    def assets(self):
        # List of assets involved in the strategy
        return [self.ticker]

    def run(self, data):
        # `data` contains the necessary historical data and current market data
        
        # Extract the latest date from the data for SPY
        latest_date = data["ohlcv"][-1][self.ticker]["date"]
        
        # Convert the date string to a Python datetime object
        from datetime import datetime
        latest_datetime = datetime.strptime(latest_date, "%Y-%m-%d")
        
        # Check if the day of the month is odd or even
        day_of_month = latest_datetime.day
        
        allocation_dict = {}
        
        if day_of_month % 2 == 0:
            # If it's an even day, set allocation to 1 (buy or hold SPY)
            allocation_dict[self.ticker] = 1
        else:
            # If it's an odd day, set allocation to 0 (sell SPY)
            allocation_dict[self.ticker] = 0
        
        # Return the target allocation object with the determined allocations
        return TargetAllocation(allocation_dict)