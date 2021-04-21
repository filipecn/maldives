import datetime
import logging
import os
import pandas as pd
from ..brokers.broker import Broker
from ..models.order import Order
from ..models.price import Price
from yahooquery import Ticker


class YQBroker(Broker):
    cache_dir: str
    ticker: Ticker

    def __init__(self):
        self.cache_dir = '../data'

    def set_asset(self, symbol: str):
        self.asset = symbol
        self.ticker = Ticker(symbol + '.SA')

    def symbol_ticker(self):
        logging.warning("symbol_ticker for YQBroker not implemented.")

    def download_history(self, start: datetime, end=None):
        cache_file = self.cache_dir + '/' + self.asset + '.sa'
        if os.path.isfile(cache_file):
            logging.info("loading from cache file: %s", cache_file)
            self.symbol_db = pd.read_csv(cache_file)
        else:
            logging.info("downloading history for: %s", self.asset)
            self.symbol_db = self.ticker.history(start=start)
            logging.info("  storing cache into %s", cache_file)
            self.symbol_db.to_csv(cache_file)
        logging.info("... loaded %d lines.", len(self.symbol_db))
        # convert date to datetime
        self.symbol_db['date'] = pd.to_datetime(self.symbol_db['date'])

    def symbol_ticker_candle(self, interval: int):
        logging.warning("symbol_ticker_candle for YQBroker not implemented.")
        pass

    def historical_symbol_ticker_candle(self, start: datetime, end=None, interval=60 * 60 * 24):
        if len(self.symbol_db) == 0:
            logging.error("download history prices first!")
        candle = self.symbol_db[self.symbol_db.date == start]
        if len(candle):
            return Price(date=start,
                         current=float(candle['open']),
                         open=float(candle['open']),
                         close=float(candle['close']),
                         low=float(candle['low']),
                         high=float(candle['high']),
                         volume=int(candle['volume']))
        return Price()

    def order(self, order: Order):
        logging.warning("order for YQBroker not implemented.")
