from datetime import datetime


class Price:
    date: datetime = datetime(1, 1, 1)
    current: float = 0
    open: float = 0
    close: float = 0
    low: float = 0
    high: float = 0
    volume: int = 0

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
