from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI, ATR, EMA
from surmount.logging import log

class ImprovedTradingStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY"]

    @property
    def interval(self):
        return "5min"

    def on_start(self):
        self.previous_macds = None
        self.previous_rsi = None
        self.logger.info("Improved Trading Strategy Initialized.")

    def run(self, data):
        """
        Execute the trading strategy for SPY with enhanced logic.

        :param data: Market data provided by the Surmount trading environment.
        :return: TargetAllocation with updated asset allocations.
        """
        holdings = data["holdings"]
        allocation = holdings.get("SPY", 0)

        # Calculate indicators
        try:
            macd_result = MACD("SPY", data["ohlcv"], 12, 26)
            rsi_values = RSI("SPY", data, 14)
            atr_value = ATR("SPY", data["ohlcv"], 14)[-1]
            ema_value = EMA("SPY", data["ohlcv"], 50)[-1]

            rsi_value = rsi_values[-1] if rsi_values else 50  # Default to neutral RSI
        except Exception as e:
            log(f"Error calculating indicators: {e}")
            return None

        # Validate MACD result
        if macd_result:
            signal_line = macd_result.get("MACDs_12_26_9", [])
            if len(signal_line) < 2:
                log("Insufficient MACD data. Skipping allocation logic.")
                return None

            current_macds = signal_line[-1]
            price = data["ohlcv"]["SPY"][-1]["close"]

            # Log the current indicator values
            log(f"MACDs Signal: {current_macds}")
            log(f"RSI Signal: {rsi_value}")
            log(f"ATR: {atr_value}, EMA: {ema_value}, Price: {price}")

            # Trend filter: Only buy if above the 50-period EMA
            if price > ema_value:
                # Enhanced allocation logic with dynamic thresholds
                if current_macds < -0.5 * atr_value and rsi_value < 35:
                    allocation = 1.0  # Full allocation
                    log("Strong buy signal: MACDs < -0.5 * ATR and RSI < 35. Allocating 100% to SPY.")
                elif current_macds > 0.6 * atr_value or rsi_value > 70:
                    allocation = 0.2  # Partial allocation
                    log("Partial allocation signal: MACDs > 0.6 * ATR or RSI > 70. Allocating 20% to SPY.")
                else:
                    log("No actionable signals. Maintaining current allocation.")
            else:
                log("Price below EMA. Reducing exposure.")
                allocation = 0.2  # Conservative allocation when price is below EMA

        # Return the target allocation
        return TargetAllocation({"SPY": allocation})
