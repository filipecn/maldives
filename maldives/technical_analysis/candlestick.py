class Candlestick:
    def __init__(self, data, index):
        self.index = index
        self.min_value = data['low']
        self.max_value = data['high']
        self.open_value = data['open']
        self.close_value = data['close']
        self.date = data['date']
