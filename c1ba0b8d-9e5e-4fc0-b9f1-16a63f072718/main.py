from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    @property
    def assets(self):
        # Defines the asset this strategy is concerned with
        return ["SPY"]

    @property
    def interval(self):
        # The interval for data collection is set to 10 minutes
        return "10min"

    def run(self, data):
        # Get the latest MACD and RSI values for the SPY
        macd_data = MACD("SPY", data["ohlcv"], 12, 26, 9)
        rsi_data = RSI("SPY", data["ohlcv"], 14)

        # Ensure there is enough data for both indicators
        if macd_data is None or rsi_data is None or len(rsi_data) < 1:
            return TargetAllocation({"SPY": 0})

        macd_signal = macd_data["signal"][-1]  # The latest MACD signal value
        rsi_value = rsi_data[-1]                # The latest RSI value

        # Decision logic for full and partial allocation
        if rsi_value < 40 or macd_signal < -0.40:
            # Scenario for full allocation: RSI < 40 or MACD signal < -0.40
            allocation = 1.0  # Full allocation
        elif rsi_value > 70 or macd_signal > 0.60:
            # Scenario for partial allocation: RSI > 70 or MACD signal > 0.60
            allocation = 0.2  # Partial allocation
        else:
            # Default scenario: no strong momentum detected
            allocation = 0.0  # No allocation

        log(f"Allocation for SPY: {allocation*100}%")

        return TargetAllocation({"SPY": allocation})