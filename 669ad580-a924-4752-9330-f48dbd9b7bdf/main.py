from surmount.technical_indicators import SMA, EMA
from surmount.base_class import Strategy

class MovingAverageCrossoverStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY"]  # Operates on SPY

    @property
    def interval(self):
        return "1hour"  # 1-hour intervals

    def on_start(self):
        # Initialize variables
        self.logger.info("Moving Average Crossover Strategy Initialized.")

    def run(self, data):
        # Extract required data
        holdings = data["holdings"]
        ohlcv = data["ohlcv"].get("SPY")

        # Ensure data is available
        if not ohlcv:
            self.logger.warning("No OHLCV data for SPY. Skipping.")
            return None

        # Calculate SMA and EMA
        try:
            sma = SMA("SPY", ohlcv, period=14)[-1]  # Latest 14-period SMA
            ema = EMA("SPY", ohlcv, period=30)[-1]  # Latest 30-period EMA
        except Exception as e:
            self.logger.error(f"Error calculating SMA/EMA: {e}")
            return None

        self.logger.info(f"SMA: {sma}, EMA: {ema}")

        # Determine allocation
        allocation = {}
        if sma > ema:
            # Bullish signal: SMA > EMA
            self.logger.info("Bullish Signal: Allocating 100% to SPY.")
            allocation["SPY"] = 1.0
        else:
            # Else condition: SMA <= EMA
            self.logger.info("Bearish/Neutral Signal: Allocating 40% to SPY.")
            allocation["SPY"] = 0.4

        # Return the target allocation
        return allocation if allocation else None
