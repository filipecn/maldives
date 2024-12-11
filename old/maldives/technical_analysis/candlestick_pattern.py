class CandlestickPattern:
    def __init__(self, symbol, timeframe, reliability, pattern, candle_time, date, status):
        self.symbol = symbol
        self.timeframe = timeframe
        self.reliability = reliability
        self.pattern = pattern
        self.candle_time = candle_time
        self.date = date
        self.status = status
