from surmount.base_class import Strategy, TargetAllocation, backtest
from surmount.technical_indicators import MACD, RSI
from surmount.logging import log

class TradingStrategy(Strategy):

   @property
   def assets(self):
      return ["SPY"]

   @property
   def interval(self):
      return "5min"

   def run(self, data):
      # Extract holdings and OHLCV data
      holdings = data["holdings"]
      data = data["ohlcv"]

      try:
         macd_data = MACD("SPY", data, fast=12, slow=26)  # Calculate MACD (12, 26)
         macd_signal_value = macd_data["MACD"][-1]
      except Exception as e:
         macd_signal_value = 0  # Default neutral MACD signal


      # Allocation logic
      allocation = {}
      if macd_signal_value < -0.40:
         allocation["SPY"] = 1.0
      elif macd_signal_value > 0.60:
         allocation["SPY"] = 0.2
      else:
         allocation["SPY"] = holdings.get("SPY", 0)

      # Check if allocation needs adjustment
      for key in allocation:
         if abs(allocation[key] - holdings.get(key, 0)) > 0.02:
            return TargetAllocation(allocation)

      return None
