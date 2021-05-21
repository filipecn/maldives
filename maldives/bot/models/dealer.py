from datetime import datetime
from abc import ABC, abstractmethod
from ..models.order import Order
from pandas import DataFrame


class Dealer(ABC):
    historical_data: DataFrame

    @abstractmethod
    def get_symbol(self, assets):
        pass

    @abstractmethod
    def get_asset_balance(self, assets):
        pass

    @abstractmethod
    def symbol_ticker(self, symbols):
        pass

    @abstractmethod
    def symbol_ticker_candle(self, symbols, interval: int):
        pass

    @abstractmethod
    def historical_symbol_ticker_candle(self, symbols, start: datetime, end=None, interval: str = ''):
        pass

    @abstractmethod
    def order(self, order: Order):
        pass
