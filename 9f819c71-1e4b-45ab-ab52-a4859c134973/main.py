from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI
from surmount.logging import log

class OptionsTradingStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY"]

    @property
    def interval(self):
        return "5min"

    def on_start(self):
        self.previous_macds = None
        self.previous_rsi = None
        self.logger.info("Options Trading Strategy Initialized.")

    def run(self, data):
        """
        Execute the trading strategy for SPY options based on MACDs and RSI.

        :param data: Market data provided by the Surmount trading environment.
        :return: TargetAllocation with updated asset allocations or option orders.
        """
        holdings = data["holdings"]

        # Get options chain data
        option_chain = data.get("options", {}).get("SPY")
        if not option_chain:
            log("No options data available for SPY. Skipping.")
            return None

        # Calculate indicators
        try:
            macd_result = MACD("SPY", data["ohlcv"], 12, 26)
            rsi_values = RSI("SPY", data, 14)

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

            # Log the current indicator values
            log(f"MACDs Signal: {current_macds}")
            log(f"RSI Signal: {rsi_value}")

            # Select at-the-money (ATM) options, closest expiration
            atm_call = next((o for o in option_chain if o["strike"] >= data["ohlcv"]["SPY"][-1]["close"] and o["right"] == "C"), None)
            atm_put = next((o for o in option_chain if o["strike"] <= data["ohlcv"]["SPY"][-1]["close"] and o["right"] == "P"), None)

            if not atm_call or not atm_put:
                log("No suitable ATM options found. Skipping.")
                return None

            # Buy logic: Strong bullish signal
            if current_macds < -0.45 and rsi_value < 35:
                log(f"Strong bullish signal: Buying 1 ATM Call {atm_call['symbol']}.")
                return [{"action": "buy", "symbol": atm_call["symbol"], "quantity": 1}]

            # Sell logic: Strong bearish signal
            elif current_macds > 0.6 or rsi_value > 70:
                log(f"Strong bearish signal: Buying 1 ATM Put {atm_put['symbol']}.")
                return [{"action": "buy", "symbol": atm_put["symbol"], "quantity": 1}]

            # No signal
            else:
                log("No actionable signals. Holding current positions.")
                return None
