import datetime
import logging
import os
import pandas as pd
from ..models.order import Order
from ..models.price import Price
from ..models.dealer import Dealer
from yahooquery import Ticker
from pandas import DataFrame


class YQBroker(Dealer):
    cache_file: str = '../data/yq_broker_data.csv'
    ticker: Ticker

    def __init__(self):
        self.historical_data = DataFrame()

    def get_symbol(self, asset):
        if type(asset) is str:
            return asset + '.sa'
        return [a + '.sa' for a in asset]

    def get_asset_balance(self, symbols):
        logging.warning("get_asset_balance not implemented for YQBroker.")
        if type(symbols) is str:
            return 0
        return len(symbols) * [0]

    def symbol_ticker(self, symbols):
        logging.warning("symbol_ticker not implemented for YQBroker.")
        if type(symbols) is str:
            return Price()
        return [Price() for _ in range(len(symbols))]

    def symbol_ticker_candle(self, symbols, interval: int):
        logging.warning("symbol_ticker_candle not implemented for YQBroker.")
        pass

    def check_symbol_history(self, symbol, start: datetime, end=None):
        print(symbol)
        logging.info("checking history for: %s", symbol)
        symbol_data = self.historical_data[self.historical_data.symbol == self.get_symbol(symbol)]
        if len(symbol_data) == 0:
            logging.info("downloading history for: %s", symbol)
            data = Ticker(symbol).history(start=start)
            data.to_csv('tmp')
            data = pd.read_csv('tmp')
            data['date'] = pd.to_datetime(data['date'])
            self.historical_data = pd.concat([self.historical_data, data], ignore_index=True)
            print(self.historical_data)

    def download_history(self, symbols, start: datetime, end=None, interval='1d'):
        self.ticker = Ticker(self.get_symbol(symbols))
        if os.path.isfile(self.cache_file):
            logging.info("loading from cache file: %s", self.cache_file)
            self.historical_data = pd.read_csv(self.cache_file)
            for s in self.get_symbol(symbols):
                self.check_symbol_history(s, start)
            self.historical_data.to_csv(self.cache_file)
        else:
            logging.info("downloading history for: {}", symbols)
            self.historical_data = self.ticker.history(start=start)
            logging.info("  storing cache into %s", self.cache_file)
            self.historical_data.to_csv(self.cache_file)
        logging.info("... loaded %d lines.", len(self.historical_data))
        if len(self.historical_data) == 0:
            logging.error("empty historical_cache after download.")
        self.historical_data = pd.read_csv(self.cache_file)
        # convert date to datetime
        self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])

    def historical_symbol_ticker_candle(self, symbols, start: datetime, end=None, interval='1d'):

        symbol_list = symbols
        if type(symbols) is str:
            symbol_list = [symbols]

        self.download_history(symbol_list, start, end, interval)

        candles = {}
        for symbol in symbol_list:
            candle_data = self.historical_data[self.historical_data.date >= start]
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
            candles[symbol] = prices
        return candles

    def order(self, order: Order):
        logging.warning("order not implemented for YQBroker.")
