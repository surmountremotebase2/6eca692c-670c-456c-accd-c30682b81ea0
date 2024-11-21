import surmount as sm

class MACDAndRSIAlgo(sm.AlgoBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Parameters
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.rsi_period = 14
        self.rsi_oversold = 30
        self.rsi_overbought = 70

        # Indicators
        self.macd = None
        self.rsi = None
        self.previous_macd_signal = None

    def on_start(self):
        # Set up indicators
        self.macd = self.add_indicator("MACD", self.macd_fast, self.macd_slow, self.macd_signal)
        self.rsi = self.add_indicator("RSI", self.rsi_period)

        self.logger.info("Algorithm started with MACD and RSI indicators.")

    def on_data(self, data):
        if not self.macd.ready or not self.rsi.ready:
            return

        macd_value = self.macd.value
        macd_signal = self.macd.signal
        rsi_value = self.rsi.value

        # Debugging
        self.logger.debug(f"MACD: {macd_value}, Signal: {macd_signal}, RSI: {rsi_value}")

        # Entry conditions
        if macd_value > macd_signal and self.previous_macd_signal <= macd_signal and rsi_value < self.rsi_oversold:
            self.buy("long", size=1)
            self.logger.info(f"Buy signal triggered: MACD crossover and RSI oversold ({rsi_value}).")

        # Exit conditions
        elif macd_value < macd_signal and self.previous_macd_signal >= macd_signal and rsi_value > self.rsi_overbought:
            self.sell("long", size=1)
            self.logger.info(f"Sell signal triggered: MACD crossover and RSI overbought ({rsi_value}).")

        # Update the previous MACD signal value
        self.previous_macd_signal = macd_signal
