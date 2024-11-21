from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["SPY", "QQQ", "VTI", "VXUS"]  # List of assets we're interested in

    @property
    def interval(self):
        return "1day"  # Set the interval to daily

    @property
    def assets(self):
        return self.tickers  # Define which assets to track

    def run(self, data):
        allocation_dict = {}
        
        # Loop through each ticker to check MACD and RSI
        for ticker in self.tickers:
            try:
                # Get MACD and RSI values for each ticker
                macd_data = MACD(ticker, data["ohlcv"], fast=12, slow=26)
                rsi_data = RSI(ticker, data["ohlcv"], length=14)
                
                # Check if MACD line crosses above the signal line and RSI is below 70
                if macd_data["MACD"][-1] > macd_data["signal"][-1] and rsi_data[-1] < 70:
                    allocation_dict[ticker] = 0.25  # allocating 25% to this asset
                else:
                    allocation_dict[ticker] = 0.0  # not allocating to this asset
            except Exception as e:
                log(f"An error occurred while processing {ticker}: {str(e)}")
                allocation_dict[ticker] = 0.0  # Default to no allocation in case of error
        
        # Implementing a simple risk management by checking if the
        # sum of allocations does not exceed 1 (100% of the portfolio)
        total_allocation = sum(allocation_dict.values())
        if total_allocation > 1:
            # Normalize allocations if the total exceeds 100%
            allocation_dict = {ticker: weight / total_allocation for ticker, weight in allocation_dict.items()}

        log(f"Allocations: {allocation_dict}")
        return TargetAllocation(allocation_dict)