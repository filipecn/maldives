from datetime import datetime
from abc import ABC, abstractmethod
from ..models.order import Order
from pandas import DataFrame


class Dealer(ABC):
    historical_data: DataFrame

    @abstractmethod
    def get_symbol_ticker(self, symbols):
        """
        Compute the actual format of symbol tickers. Different APIs may use
        different naming formats for the same symbol. Since the historical_data
        dataframe is populated with the ticker name used by the API, this function
        must be used before accessing the base.

        For example, the symbol 'petr4' under the yahoo finance API receives
        the ticker 'PETR4.sa'

        :param symbols:     str or [str]. A str of a single symbol or a [str] of
                            multiple symbols.
        :return:    str or [str]. The ticker respective to the given symbol.
                    If multiple symbols are given, then a list [] of tickers in
                    the same order is returned instead.
        """
        pass

    @abstractmethod
    def get_asset_balance(self, assets):
        """

        :param assets:
        :return:
        """
        pass

    @abstractmethod
    def symbol_ticker(self, symbols):
        """

        :param symbols:     str or [str]. A str of a single symbol or a [str] of
                            multiple symbols.
        :return:    The current price based on datetime.now() of the given symbol.
                    A dictionary of symbol -> price is returned.

        """
        pass

    @abstractmethod
    def symbol_ticker_candle(self, symbols, interval, start: datetime):
        """

        :param symbols:     str or [str]. A str of a single symbol or a [str] of
                            multiple symbols.
        :param interval:    str or int. A str naming the candle size ('1d', '1m', etc) or
                            an int representing the candle size in seconds.
        :param start:       Candle open time.

        :return:    A single candle object representing the given period for the
                    given symbol. If multiple symbols are given, then a dictionary
                    of symbol - > candle is returned instead.
        """
        pass

    @abstractmethod
    def order(self, order: Order):
        """

        :param order:
        :return:
        """
        pass

    @abstractmethod
    def historical_candle_series(self, symbols, start: datetime, end, interval):
        """

        :param symbols:     str or [str]. A str of a single symbol or a [str] of
                            multiple symbols.
        :param start:       First candle open time.
        :param end:         Last candle close time.
        :param interval:    str or int. A str naming the individual candle size ('1d', '1m', etc)
                            or an int representing the individual candle size in seconds.
        :return:    A dictionary per given symbol containing the list of historical
                    candles and a TA object built from the computed series. If
                    multiple symbols are given, then a dictionary of
                    symbol -> dictionary is returned instead.
        """
        pass
