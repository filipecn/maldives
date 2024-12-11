class Order:
    BUY = 'BUY'
    SELL = 'SELL'

    TYPE_LIMIT = 'LIMIT'
    TYPE_MARKET = 'MARKET'
    TYPE_STOP_LOSS = 'STOP_LOSS'
    TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
    TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

    type: str = TYPE_LIMIT
    symbol: str = ''
    price: float = 0
    quantity: int = 0

    def __init__(self, **kwargs):
        # super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)
