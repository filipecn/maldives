class Candlestick:
    def __init__(self, data, index):
        self.index = index
        self.min_value = data['Low']
        self.max_value = data['High']
        self.open_value = data['Open']
        self.close_value = data['Close']
        self.date = data['Date']
