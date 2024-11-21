from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define tickers to monitor
        self.tickers = ["SPY", "VTI", "VXUS"]
        
    @property
    def interval(self):
        # Using daily interval for analysis
        return "1day"
    
    @property
    def assets(self):
        # We're interested in trading SPY based on the condition of all assets
        return ["SPY"]
    
    def run(self, data):
        # Initialize allocation with no investment
        allocation_dict = {"SPY": 0.0}

        # Conditions for trading based on MACD and RSI for each ticker
        for ticker in self.tickers:
            macd_signal = MACD(ticker, data["ohlcv"], fast=12, slow=26)["signal"]
            rsi_value = RSI(ticker, data["ohlcv"], length=14)
            
            if len(macd_signal) > 0 and len(rsi_value) > 0:
                macd_latest = macd_signal[-1]
                rsi_latest = rsi_value[-1]
                
                # Example conditions: MACD > 0 signifies a bullish trend, 
                # RSI < 30 is considered oversold (buy signal),
                # RSI > 70 is considered overbought (sell signal)
                if macd_latest > 0 and rsi_latest < 30:
                    # Buy signal
                    allocation_dict["SPY"] = 1.0
                    log(f"Buying SPY based on signals from {ticker}")
                elif rsi_latest > 70:
                    # Sell/avoid buying signal
                    allocation_dict["SPY"] = 0.0
                    log(f"Avoiding/Reducing SPY based on signals from {ticker}")
                
                # Log for analysis
                log(f"{ticker} - MACD: {macd_latest}, RSI: {rsi_latest}")
        
        # Return our allocation decision
        return TargetAllocation(allocation_dict)