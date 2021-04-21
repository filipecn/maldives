import datetime
from pandas import DataFrame
from abc import ABC, abstractmethod
from ..models.order import Order


class Broker(ABC):
    asset: str = ''
    asset_balance: float = 0
    symbol_db: DataFrame

    def get_symbol(self):
        return self.asset

    def set_asset(self, symbol: str):
        self.asset = symbol

    def get_asset_balance(self):
        return self.asset_balance

    def set_asset_balance(self, balance: float):
        self.asset_balance = balance

    @abstractmethod
    def symbol_ticker(self):
        pass

    @abstractmethod
    def download_history(self, start: datetime, end: datetime):
        pass

    @abstractmethod
    def symbol_ticker_candle(self, interval: int):
        pass

    @abstractmethod
    def historical_symbol_ticker_candle(self, start: datetime, end=None, interval=60):
        pass

    @abstractmethod
    def order(self, order: Order):
        pass
