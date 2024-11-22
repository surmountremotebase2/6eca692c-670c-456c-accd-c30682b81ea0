from surmount.base_class import Strategy, TargetAllocation, backtest
from surmount.technical_indicators import MACD, RSI
from surmount.logging import log

class TradingStrategy(Strategy):

   @property
   def assets(self):
      return ["SPY"]

   @property
   def interval(self):
      return "1day"

   def run(self, data):
      # Extract holdings and OHLCV data
      holdings = data["holdings"]
      data = data["ohlcv"]

      # Initialize indicators
      try:
         rsi_value = RSI("SPY", data, 14)[-1]  # Calculate RSI (14-period)
      except:
         rsi_value = 50  # Default neutral RSI

      try:
         macd_data = MACD("SPY", data, fast=12, slow=26)  # Calculate MACD (12, 26)
         macd_line = macd_data.get("macd", [])
         signal_line = macd_data.get("signal", [])
         macd_signal_value = signal_line[-1] if signal_line else 0
      except Exception as e:
         log.warning(f"Error calculating MACD: {e}. Defaulting to 0.")
         macd_signal_value = 0  # Default neutral MACD signal


      # Allocation logic
      allocation = {}
      if rsi_value < 40 and macd_signal_value < -0.40:
         allocation["SPY"] = 1.0
      elif rsi_value > 70 and macd_signal_value > 0.60:
         allocation["SPY"] = 0.2
      else:
         allocation["SPY"] = holdings.get("SPY", 0)

      # Check if allocation needs adjustment
      for key in allocation:
         if abs(allocation[key] - holdings.get(key, 0)) > 0.02:
            return TargetAllocation(allocation)

      return None
