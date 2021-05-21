from datetime import datetime


class Price:
    date: datetime = datetime(1, 1, 1)
    currency: str = 'BRL'
    symbol: str = ''
    current: float = 0
    open: float = 0
    close: float = 0
    low: float = 0
    high: float = 0
    volume: float = 0
    interval: str = ''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
