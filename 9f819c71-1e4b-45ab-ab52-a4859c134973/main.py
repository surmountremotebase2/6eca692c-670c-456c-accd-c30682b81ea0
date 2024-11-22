from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY"]

    @property
    def interval(self):
        return "5min"

    def run(self, data):
        holdings = data["holdings"]
        allocation = holdings.get("SPY", 0)

        macd_result = MACD("SPY", data["ohlcv"], 12, 26)
        rsi_value = RSI("SPY", data, 14)[-1]
        atr_value = ATR("SPY", data["ohlcv"], 14)[-1]

        if macd_result:
            signal_line = macd_result.get("MACDs_12_26_9", [])
            if len(signal_line) > 1:
                current_macds = signal_line[-1]
                log(f"MACDs Signal: {current_macds}, RSI: {rsi_value}, ATR: {atr_value}")

                # Dynamic thresholds
                macd_lower = -0.5 * atr_value
                macd_upper = 0.5 * atr_value

                if current_macds < macd_lower and rsi_value < 35:
                    allocation = 1.0  # Full allocation to SPY
                    log("MACDs < Lower Threshold and RSI < 35: Allocating 100% to SPY.")
                elif current_macds > macd_upper or rsi_value > 70:
                    allocation = 0.2  # Partial allocation to SPY
                    log("MACDs > Upper Threshold or RSI > 70: Allocating 20% to SPY.")
                elif rsi_value > 50 and rsi_value <= 60 and current_macds > 0:
                    allocation = 0.5  # Medium allocation
                    log("Moderate RSI and MACDs positive: Allocating 50% to SPY.")
                else:
                    log("No significant signals. Maintaining current allocation.")

        return TargetAllocation({"SPY": allocation})
