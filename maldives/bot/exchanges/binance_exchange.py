from datetime import datetime, timezone
import logging
import os
import pandas as pd
from ..models.order import Order
from ..models.price import Price
from ..models.dealer import Dealer
from pandas import DataFrame

from binance.client import Client
from binance.enums import *
from binance.websockets import BinanceSocketManager


def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000


class BinanceExchange(Dealer):
    currency: str

    def __init__(self, key: str, secret: str):
        self.apiKey = key
        self.apiSecret = secret
        self.socketManager = None
        self.socket = None
        self.currency = ''
        logging.info("connecting to binance api ...")
        self.client = Client(self.apiKey, self.apiSecret)
        logging.info("... done")
        self.name = self.__class__.__name__

    def set_currency(self, symbol: str):
        self.currency = symbol

    def compute_symbol_pair(self, asset):
        if type(asset) is str:
            return asset + self.currency
        return [a + self.currency for a in asset]

    def get_symbol(self, asset):
        return self.compute_symbol_pair(asset)

    def _single_symbol_ticker(self, symbol: str):
        response = self.client.get_symbol_ticker(symbol=self.compute_symbol_pair(symbol))
        return Price(currency=self.currency, symbol=symbol, current=response['price'], date=datetime.now())

    def symbol_ticker(self, symbols):
        if type(symbols) is str:
            return self._single_symbol_ticker(symbols)
        return [self._single_symbol_ticker(symbol) for symbol in symbols]

    def _single_asset_balance(self, asset):
        response = self.client.get_asset_balance(asset=asset)
        return response['free']

    def get_asset_balance(self, assets):
        if type(assets) is str:
            return self._single_asset_balance(assets)
        return [self._single_asset_balance(asset) for asset in assets]

    def _single_symbol_ticker_candle(self, symbol, interval_enum):
        return self.client.get_klines(symbol=symbol, interval=interval_enum)

    def symbol_ticker_candle(self, symbols, interval: str):
        pairs = self.compute_symbol_pair(symbols)
        interval_enum = interval  # check if interval is valid
        if type(symbols) is str:
            return self._single_symbol_ticker_candle(pairs, interval_enum)
        return [self._single_symbol_ticker_candle(pair, interval_enum) for pair in pairs]

    def _single_historical_symbol_ticker_candle(self, symbol, start: datetime, end=None, interval: str = '1d'):
        if end:
            end = int(unix_time_millis(end))
        pair = self.compute_symbol_pair(symbol)
        output = []
        for candle in self.client.get_historical_klines_generator(pair, interval,
                                                                  int(unix_time_millis(start)), end):
            """
                [
                    [
                        1499040000000,      0# Open time
                        "0.01634790",       1# Open
                        "0.80000000",       2# High
                        "0.01575800",       3# Low
                        "0.01577100",       4# Close
                        "148976.11427815",  5# Volume
                        1499644799999,      # Close time
                        "2434.19055334",    # Quote asset volume
                        308,                # Number of trades
                        "1756.87402397",    # Taker buy base asset volume
                        "28.46694368",      # Taker buy quote asset volume
                        "17928899.62484339" # Can be ignored
                    ]
                ]
            """
            date = datetime.fromtimestamp(int(candle[0]) / 1000)
            open_price = float(candle[1])
            high = float(candle[2])
            low = float(candle[3])
            close = float(candle[4])
            volume = float(candle[5])
            self.historical_data.loc[len(self.historical_data) + 1] = [pair, date, close, open_price, low, high, volume,
                                                                       interval]
            output.append(
                Price(pair=pair, currency=self.currency, symbol=symbol,
                      current=open_price, low=low, high=high, volume=volume, close=close, open=open_price,
                      date=date, interval=interval)
            )
        return output

    def historical_symbol_ticker_candle(self, symbols, start: datetime, end=None, interval: str = ''):
        self.historical_data = DataFrame(
            columns=['symbol', 'date', 'close', 'open', 'low', 'high', 'volume', 'interval'])
        self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])
        self.historical_data['close'] = pd.to_numeric(self.historical_data['close'])
        self.historical_data['open'] = pd.to_numeric(self.historical_data['open'])
        self.historical_data['low'] = pd.to_numeric(self.historical_data['low'])
        self.historical_data['high'] = pd.to_numeric(self.historical_data['high'])
        self.historical_data['volume'] = pd.to_numeric(self.historical_data['volume'])
        if type(symbols) is str:
            return self._single_historical_symbol_ticker_candle(symbols, start, end, interval)
        candles = {}
        for symbol in symbols:
            candles[symbol] = self._single_historical_symbol_ticker_candle(symbol, start, end, interval)
        return candles

    def order(self, order: Order):
        pass
