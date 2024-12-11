from datetime import datetime, timedelta
import logging
import os
import pandas as pd
from ..models.order import Order
from ..models.price import Price
from ..models.dealer import Dealer
from pandas import DataFrame
from maldives.technical_analysis import TA

from binance.client import Client
from binance.enums import *
from binance.websockets import BinanceSocketManager


def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000


class BinanceExchange(Dealer):
    currency: str
    cache_file: str = '../data/binance_data.csv'

    def __init__(self, key: str, secret: str, logger):
        self.historical_data = DataFrame()
        self.logger = logger
        self.apiKey = key
        self.apiSecret = secret
        self.socketManager = None
        self.socket = None
        self.currency = ''
        logger.log_info("connecting to binance api ...")
        self.client = Client(self.apiKey, self.apiSecret)
        logger.log_info("... done")
        self.name = self.__class__.__name__

    def set_currency(self, symbol: str):
        self.currency = symbol

    def compute_symbol_pair(self, asset):
        if type(asset) is str:
            return asset + self.currency
        return [a + self.currency for a in asset]

    def get_symbol_ticker(self, asset):
        return self.compute_symbol_pair(asset)

    def _single_symbol_ticker(self, symbol: str):
        response = self.client.get_symbol_ticker(symbol=self.compute_symbol_pair(symbol))
        return Price(currency=self.currency, symbol=symbol, current=response['price'], date=datetime.now())

    def symbol_ticker(self, symbols):
        r = {}
        if type(symbols) is str:
            r[symbols] = self._single_symbol_ticker(symbols)
        else:
            for symbol in symbols:
                r[symbol] = self._single_symbol_ticker(symbol)
        return r

    def _single_asset_balance(self, asset):
        response = self.client.get_asset_balance(asset=asset)
        return response['free']

    def get_asset_balance(self, assets):
        if type(assets) is str:
            return self._single_asset_balance(assets)
        return [self._single_asset_balance(asset) for asset in assets]

    def _single_symbol_ticker_candle(self, symbol, interval_enum):
        return self.client.get_klines(symbol=symbol, interval=interval_enum)

    def symbol_ticker_candle(self, symbols, interval, start: datetime):
        pairs = self.compute_symbol_pair(symbols)
        interval_enum = interval  # check if interval is valid
        if type(symbols) is str:
            return self._single_symbol_ticker_candle(pairs, interval_enum)
        return [self._single_symbol_ticker_candle(pair, interval_enum) for pair in pairs]

    def _single_historical_symbol_ticker_candle(self, symbol, start: datetime, end=None, interval: str = '1d'):
        if not end:
            # end = int(unix_time_millis(end))
            end = datetime.today()
        # convert to binance timezone
        start += timedelta(hours=3)
        end += timedelta(hours=3)
        # format to binance date string
        start_str = start.strftime("%m/%d/%Y, %H:%M:%S")
        end_str = end.strftime("%m/%d/%Y, %H:%M:%S")

        pair = self.compute_symbol_pair(symbol)

        self.logger.log_info('Downloading pair %s, interval %s, from %s to %s' % (pair, interval, start_str, end_str))

        output = []
        for candle in self.client.get_historical_klines_generator(pair, interval, start_str, end_str):
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
            row = {
                'symbol': pair,
                'date': datetime.fromtimestamp(int(candle[0]) / 1000),
                'close': float(candle[4]),
                'open': float(candle[1]),
                'low': float(candle[3]),
                'high': float(candle[2]),
                'volume': float(candle[5]),
                'interval': interval
            }
            self.historical_data = self.historical_data.append(row, ignore_index=True)

    def check_symbol_history(self, symbol, start: datetime, end: datetime, interval: str):
        self.logger.log_info("checking history for pair: %s from %s to %s" % (symbol, str(start), str(end)))
        if len(self.historical_data) == 0:
            self.logger.log_info("empty cache, downloading history for: %s" % symbol)
            self._single_historical_symbol_ticker_candle(symbol, start, end, interval)
            return
        symbol_data = \
            self.historical_data[(self.historical_data.symbol == self.get_symbol_ticker(symbol)) & (
                    self.historical_data['interval'] == interval)]
        self.logger.log_debug('CHECK %s %s %s %s' % (str(start), str(end), str(symbol_data['date'].min()),
                                                     str(symbol_data['date'].max())))
        if len(symbol_data) == 0 or symbol_data['date'].min() > start or symbol_data['date'].max() < end:
            self.logger.log_info("check failed, downloading history for: %s" % symbol)
            self._single_historical_symbol_ticker_candle(symbol, start, end, interval)

    def download_history(self, symbols, start: datetime, end: datetime, interval: str):
        if os.path.isfile(self.cache_file):
            self.logger.log_info("loading from cache file: %s" % self.cache_file)
            self.historical_data = pd.read_csv(self.cache_file)
            self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])

        for s in symbols:
            self.check_symbol_history(s, start, end, interval)

        self.logger.log_info("  storing cache into %s" % self.cache_file)
        self.historical_data.drop_duplicates().reset_index(drop=True).to_csv(self.cache_file, index=False)

        if len(self.historical_data) == 0:
            logging.error("empty historical_cache after download.")

        self.historical_data = pd.read_csv(self.cache_file).drop_duplicates()
        self.logger.log_info("... loaded %d lines." % len(self.historical_data))
        # convert date to datetime
        self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])

    def historical_candle_series(self, symbols, start: datetime, end, interval):

        candles = {}

        symbol_list = symbols
        if type(symbols) is str:
            symbol_list = [symbols]

        self.download_history(symbol_list, start, end, interval)

        for symbol in symbol_list:
            candle_data = self.historical_data[self.historical_data.symbol == self.get_symbol_ticker(symbol)]
            candle_data = candle_data[candle_data.interval == interval]
            candle_data = candle_data[candle_data.date >= start]
            candle_data = candle_data[candle_data.date <= end]
            prices = []
            for _, candle in candle_data.iterrows():
                prices.append(Price(date=candle['date'],
                                    symbol=candle['symbol'],
                                    current=float(candle['open']),
                                    open=float(candle['open']),
                                    close=float(candle['close']),
                                    low=float(candle['low']),
                                    high=float(candle['high']),
                                    volume=float(candle['volume']),
                                    interval=interval))
            candles[symbol] = {
                "prices": prices,
                "ta": TA(candle_data)
            }
        return candles

    def order(self, order: Order):
        pass
