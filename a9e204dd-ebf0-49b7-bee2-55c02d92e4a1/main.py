from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI, EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    # Define the assets this strategy will trade
    @property
    def assets(self):
        return ["SPY"]

    # Set the interval for the data. This strategy uses 5-minute intervals.
    @property
    def interval(self):
        return "5min"

    def run(self, data):
        """
        Execute the trading strategy for SPY based on MACD, RSI, and EMA.

        :param data: The market data provided by the Surmount trading environment.
        :return: A TargetAllocation object defining the target allocations for the assets.
        """
        # Initialize allocation to the current holdings or default to 0
        holdings = data["holdings"]
        allocation = holdings.get("SPY", 0)

        # Compute indicators
        macd_result = MACD("SPY", data["ohlcv"], 12, 26)
        rsi_result = RSI("SPY", data, 14)
        ema_50 = EMA("SPY", data["ohlcv"], 50)[-1] if EMA("SPY", data["ohlcv"], 50) else None
        current_price = data["ohlcv"]["SPY"][-1]["close"]

        if macd_result and rsi_result and ema_50:
            # Extract MACD and Signal Line
            signal_line = macd_result.get("MACDs_12_26_9", [])
            macd_line = macd_result.get("MACD_12_26_9", [])
            rsi_data = rsi_result[-3:]

            # Calculate RSI slope
            rsi_slope = (rsi_data[-1] - rsi_data[0]) / 2

            # Calculate MACD difference
            current_diff = macd_line[-1] - signal_line[-1]
            previous_diff = macd_line[-2] - signal_line[-2]

            # Trend filter: only buy if price > EMA(50)
            if current_price > ema_50:
                # Bullish crossover: MACD crosses above Signal
                if macd_line[-2] < signal_line[-2] and macd_line[-1] > signal_line[-1]:
                    log("Bullish crossover detected: Allocating to SPY.")
                    allocation = min(1.0, allocation + 0.2)  # Gradual increase in allocation
            else:
                log("Price below EMA(50): Avoiding bullish trades.")

            # Bearish convergence: MACD moves closer to Signal
            if current_diff > 0 and previous_diff > current_diff:
                log("Bearish convergence detected: Reducing SPY allocation.")
                allocation = max(0.0, allocation - 0.2)  # Gradual reduction in allocation

            # Incorporate RSI slope
            if rsi_slope < -5:
                log("RSI indicates strong bearish momentum: Reducing allocation to SPY.")
                allocation = 0.0
            elif rsi_slope > 5:
                log("RSI indicates strong bullish momentum: Increasing allocation to SPY.")
                allocation = 1.0

        return TargetAllocation({"SPY": allocation})
