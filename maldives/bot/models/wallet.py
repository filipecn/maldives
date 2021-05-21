import os
import pandas as pd
from datetime import datetime
from maldives.technical_analysis import TA
from maldives.bot.models.dealer import Dealer
from pandas import DataFrame


class Wallet:
    cache_file: str = '../data/transactions.csv'
    data: DataFrame
    assets: {}

    def __init__(self):
        self.data = DataFrame(columns=['date', 'symbol', 'type', 'amount', 'price'])
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.assets = {}
        self.load_cache()

    def __del__(self):
        self.save_cache()

    def save_cache(self):
        self.data.to_csv(self.cache_file)

    def load_cache(self):
        if os.path.isfile(self.cache_file):
            self.data = pd.read_csv(self.cache_file)
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.update_assets()

    def register(self, date: datetime, symbol: str, transaction_type: str, asset_value: float, price: float):
        """
        Appends transaction to data base
        :param date: time of transaction
        :param symbol: PETR4, BTC, ...
        :param transaction_type: BUY, SELL
        :param asset_value: amount of asset in transaction
        :param price: asset's unit price
        :return:
        """
        self.data = self.data.append(
            {'date': date,
             'symbol': symbol,
             'type': transaction_type,
             'amount': asset_value,
             'price': price}, ignore_index=True)

    def update_assets(self):
        self.assets = {}
        for _, row in self.data.iterrows():
            if row['symbol'] not in self.assets:
                self.assets[row['symbol']] = {
                    'amount': 0,
                    'balance': 0,
                    'mean_price': 0
                }
            mean_price = self.assets[row['symbol']]['mean_price']
            amount = self.assets[row['symbol']]['amount']
            if row['type'] == 'BUY':
                self.assets[row['symbol']]['mean_price'] = (mean_price * amount + row['price'] * row['amount']) / (
                        amount + row['amount'])
                self.assets[row['symbol']]['amount'] += row['amount']
                self.assets[row['symbol']]['balance'] -= row['amount'] * row['price']
            else:
                self.assets[row['symbol']]['amount'] -= row['amount']
                self.assets[row['symbol']]['balance'] += row['amount'] * row['price']
        # clean zero amounts
        self.assets = {key: value for key, value in self.assets.items() if value['amount'] != 0}

    def balance(self, symbol: str = ''):
        if symbol == '':
            s = 0.0
            for _, value in self.assets.items():
                s += value['balance']
            return s
        if symbol not in self.assets:
            return 0
        return self.assets[symbol]['balance']

    def allocation_pct(self, symbol: str):
        if symbol not in self.assets:
            return 0
        s = 0.0
        for _, value in self.assets.items():
            s += value['mean_price'] * value['amount']
        return self.assets[symbol]['mean_price'] * self.assets[symbol]['amount'] / s * 100

    def backtrace(self, dealer: Dealer, start: datetime, end=None):
        asset_symbols = [a[0] for a in self.assets]
        dealer.historical_symbol_ticker_candle(asset_symbols, start, end)
        total_value = self.value()
        results = {}
        for asset in self.assets:
            ta = TA(dealer.historical_data[dealer.historical_data.symbol == dealer.get_symbol(asset[0])])
            pct_change = ta.single_pct_change()
            final_value = asset[1] + asset[1] * pct_change / 100.0
            results[asset[0]] = {
                "change": (pct_change, final_value),
                "max": (ta.max_in_range()[0], ta.max_pct_in_range()[0], ta.max_in_range()[1])
            }
            total_value += final_value - asset[1]
        results['total'] = (total_value, (total_value - self.value()) / self.value() * 100.0)
        return results
