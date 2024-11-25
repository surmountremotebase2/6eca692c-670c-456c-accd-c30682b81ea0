from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI, BB, EMA, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY"]

    @property
    def interval(self):
        return "5min"

    def on_start(self):
        """
        Initialize the strategy.
        """
        self.current_signal = "neutral"  # Track the current signal
        self.holding_period = 0  # Initialize the holding period counter

    def run(self, data):
        """
        Execute the trading strategy for SPY with multiple indicators.

        :param data: Market data provided by the Surmount trading environment.
        :return: TargetAllocation with updated asset allocations.
        """
        # Ensure holding_period and current_signal exist
        if not hasattr(self, "holding_period"):
            self.holding_period = 0
        if not hasattr(self, "current_signal"):
            self.current_signal = "neutral"

        holdings = data["holdings"]
        allocation = holdings.get("SPY", 0)

        # Compute indicators
        macd_result = MACD("SPY", data["ohlcv"], 12, 26)
        rsi_result = RSI("SPY", data, 14)
        ema_50 = EMA("SPY", data["ohlcv"], 50)[-1] if EMA("SPY", data["ohlcv"], 50) else None
        ema_200 = EMA("SPY", data["ohlcv"], 200)[-1] if EMA("SPY", data["ohlcv"], 200) else None
        bollinger_bands = BB("SPY", data["ohlcv"], 20, 2)
        atr = ATR("SPY", data["ohlcv"], 14)[-1] if ATR("SPY", data["ohlcv"], 14) else None
        current_price = data["ohlcv"][-1]["SPY"]["close"]  # Extract current price

        if macd_result and rsi_result and ema_50 and ema_200 and bollinger_bands and atr:
            # Extract MACD, RSI, and Bollinger Bands
            signal_line = macd_result.get("MACDs_12_26_9", [])
            macd_line = macd_result.get("MACD_12_26_9", [])
            rsi_value = rsi_result[-1]
            upper_band = bollinger_bands["upper"][-1]
            lower_band = bollinger_bands["lower"][-1]

            # Debugging indicator values
            log(f"Price: {current_price}, EMA(50): {ema_50}, EMA(200): {ema_200}")
            log(f"MACD: {macd_line[-1]}, Signal: {signal_line[-1]}, RSI: {rsi_value}")
            log(f"Bollinger Upper: {upper_band}, Lower: {lower_band}, ATR: {atr}")

            # Trend confirmation
            bullish_trend = ema_50 > ema_200
            bearish_trend = ema_50 < ema_200

            # Increment holding period
            self.holding_period += 1

            # Entry conditions
            if (
                macd_line[-1] > signal_line[-1]  # MACD bullish
                and current_price > lower_band  # Above lower Bollinger Band
                and rsi_value < 60  # RSI not overbought
                and bullish_trend  # Confirm bullish trend
            ):
                if self.current_signal != "bullish" or self.holding_period >= 10:
                    log("Strong bullish signal detected: Allocating 100% to SPY.")
                    allocation = min(1.0, allocation + 0.3)  # Gradual increase
                    self.current_signal = "bullish"
                    self.holding_period = 0

            # Exit or bearish conditions
            elif (
                macd_line[-1] < signal_line[-1]  # MACD bearish
                and current_price < upper_band  # Below upper Bollinger Band
                and rsi_value > 40  # RSI not oversold
                and bearish_trend  # Confirm bearish trend
            ):
                if self.current_signal != "bearish" or self.holding_period >= 10:
                    log("Strong bearish signal detected: Reducing allocation to SPY.")
                    allocation = max(0.0, allocation - 0.3)  # Gradual decrease
                    self.current_signal = "bearish"
                    self.holding_period = 0

            # No actionable signal
            else:
                log(f"No strong signal detected. Maintaining allocation: {allocation}. Holding period: {self.holding_period}")

        return TargetAllocation({"SPY": allocation})
