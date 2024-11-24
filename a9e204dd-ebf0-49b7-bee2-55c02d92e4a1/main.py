from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, RSI, ATR
from surmount.logging import log

class ImprovedTradingStrategy(Strategy):
    @property
    def assets(self):
        return ["SPY"]

    @property
    def interval(self):
        return "5min"

    def on_start(self):
        self.entry_price = None
        self.trailing_stop = None
        self.profit_target = None

    def run(self, data):
        """
        Execute the trading strategy for SPY with dynamic stop-loss and profit target.

        :param data: Market data provided by the Surmount trading environment.
        :return: TargetAllocation with updated asset allocations.
        """
        holdings = data["holdings"]
        allocation = holdings.get("SPY", 0)

        # Compute indicators
        macd_result = MACD("SPY", data["ohlcv"], 12, 26)
        rsi_result = RSI("SPY", data, 14)
        atr = ATR("SPY", data["ohlcv"], 14)[-1] if ATR("SPY", data["ohlcv"], 14) else None
        current_price = data["ohlcv"][-1]["SPY"]["close"]

        if macd_result and rsi_result and atr:
            # Extract MACD and Signal Line
            signal_line = macd_result.get("MACDs_12_26_9", [])
            macd_line = macd_result.get("MACD_12_26_9", [])
            rsi_value = rsi_result[-1]

            # Check for bullish crossover
            if macd_line[-2] < signal_line[-2] and macd_line[-1] > signal_line[-1] and rsi_value < 70:
                if self.entry_price is None:  # Enter trade
                    log("Bullish crossover detected: Entering SPY.")
                    allocation = 1.0
                    self.entry_price = current_price
                    self.trailing_stop = current_price - 2 * atr
                    self.profit_target = current_price + 2 * atr
                else:
                    log("Already in a trade, maintaining allocation.")

            # Check for bearish convergence
            elif macd_line[-2] > signal_line[-2] and macd_line[-1] < signal_line[-1]:
                log("Bearish signal detected: Exiting SPY.")
                allocation = 0.0
                self.entry_price = None
                self.trailing_stop = None
                self.profit_target = None

            # Manage open positions
            elif self.entry_price:
                # Update trailing stop
                self.trailing_stop = max(self.trailing_stop, current_price - 2 * atr)
                log(f"Trailing Stop Updated: {self.trailing_stop}")

                # Exit if trailing stop or profit target hit
                if current_price <= self.trailing_stop:
                    log("Trailing stop hit: Exiting SPY.")
                    allocation = 0.0
                    self.entry_price = None
                    self.trailing_stop = None
                    self.profit_target = None
                elif current_price >= self.profit_target:
                    log("Profit target reached: Exiting SPY.")
                    allocation = 0.0
                    self.entry_price = None
                    self.trailing_stop = None
                    self.profit_target = None

        return TargetAllocation({"SPY": allocation})
