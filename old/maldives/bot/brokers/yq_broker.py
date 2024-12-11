from datetime import datetime, timedelta
import logging
import os
import pandas as pd
from ..models.order import Order
from ..models.price import Price
from ..models.dealer import Dealer
from yahooquery import Ticker
from pandas import DataFrame
from maldives.technical_analysis import TA


class YQBroker(Dealer):
    cache_file: str = '../data/yq_broker_data.csv'
    ticker: Ticker

    def __init__(self):
        self.historical_data = DataFrame()

    def get_symbol_ticker(self, asset):
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

    def symbol_ticker_candle(self, symbols, interval, start: datetime):
        logging.warning("symbol_ticker_candle not implemented for YQBroker.")
        pass

    def check_symbol_history(self, symbol, start: datetime, end: datetime):
        logging.info("checking history for: %s", symbol)
        symbol_data = self.historical_data[self.historical_data.symbol == symbol]
        if len(symbol_data) == 0 or symbol_data['date'].min() > start or symbol_data['date'].max() < end:
            logging.info("check failed, downloading history for: %s", symbol)
            data = Ticker(symbol).history(start=start).reset_index(drop=False)
            data['date'] = pd.to_datetime(data['date'])
            self.historical_data = pd.concat([self.historical_data, data], ignore_index=True).drop_duplicates()

    def download_history(self, symbols, start: datetime, end: datetime, interval='1d'):
        if os.path.isfile(self.cache_file):
            logging.info("loading from cache file: %s", self.cache_file)
            self.historical_data = pd.read_csv(self.cache_file)
            self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])
            for s in self.get_symbol_ticker(symbols):
                self.check_symbol_history(s, start, end)
        else:
            logging.info("cache not found, downloading history for: %s", symbols)
            self.ticker = Ticker(self.get_symbol_ticker(symbols))
            self.historical_data = self.ticker.history(start=start).reset_index(drop=False)

        logging.info("  storing cache into %s", self.cache_file)
        self.historical_data.drop_duplicates().reset_index(drop=True).to_csv(self.cache_file, index=False)

        if len(self.historical_data) == 0:
            logging.error("empty historical_cache after download.")

        self.historical_data = pd.read_csv(self.cache_file).drop_duplicates()
        logging.info("... loaded %d lines.", len(self.historical_data))
        # convert date to datetime
        self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])

    def historical_candle_series(self, symbols, start: datetime, end=None, interval: str = '1d'):
        if end is None:
            end = datetime.today()
            if end.isoweekday() > 5:
                end -= timedelta(days=end.isoweekday() - 5)
                end = end.replace(hour=0, minute=0, second=0, microsecond=0)

        symbol_list = symbols
        if type(symbols) is str:
            symbol_list = [symbols]

        self.download_history(symbol_list, start, end, interval)

        candles = {}
        for symbol in symbol_list:
            candle_data = self.historical_data[self.historical_data.symbol == self.get_symbol_ticker(symbol)]
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
        logging.warning("order not implemented for YQBroker.")
