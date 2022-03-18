import os
import pandas as pd
from datetime import datetime
from maldives.technical_analysis import TA
from maldives.bot.models.dealer import Dealer
from pandas import DataFrame
import logging


class Wallet:
    data: DataFrame
    assets: {}
    cash: float

    def __init__(self):
        self.data = DataFrame(columns=['date', 'symbol', 'type', 'amount', 'price'])
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.assets = {}
        self.cash = 0

    def log(self):
        logging.info('Wallet   ******************************************************')
        logging.info('                                cash: %.2f', self.cash)
        logging.info('                                total balance: %.2f', self.balance())
        for symbol, values in self.assets.items():
            logging.info('%.2f%% Symbol: %s  Amount: %.2f  Price: %.2f  Balance: %.2f' % (
                self.allocation_pct(symbol),
                symbol, values['amount'], values['mean_price'], values['balance']))

    def save_cache(self, cache_file):
        self.data.to_csv(cache_file)

    def process_transaction(self, transaction_type: str, symbol: str, price: float, amount: float):
        if symbol not in self.assets:
            self.assets[symbol] = {
                'amount': amount,
                'balance': -amount * price,
                'mean_price': price
            }
            if transaction_type == 'SELL':
                self.cash += price * amount
                self.assets[symbol]['amount'] *= -1
                self.assets[symbol]['balance'] *= -1
            else:
                self.cash -= price * amount
        else:
            mean_price = self.assets[symbol]['mean_price']
            current_amount = self.assets[symbol]['amount']
            if transaction_type == 'BUY':
                self.assets[symbol]['mean_price'] = (mean_price * current_amount + price * amount) / (
                        current_amount + amount)
                self.assets[symbol]['amount'] += amount
                self.assets[symbol]['balance'] -= amount * price
                self.cash -= price * amount
            else:
                self.cash += price * amount
                self.assets[symbol]['amount'] -= amount
                self.assets[symbol]['balance'] += amount * price

    def register(self, date: datetime, symbol: str, transaction_type: str, price: float, amount: float):
        """
        Appends transaction to data base
        :param date: time of transaction
        :param symbol: PETR4, BTC, ...
        :param transaction_type: BUY, SELL
        :param amount: asset amount in transaction
        :param price: asset's unit price
        :return:
        """
        self.data = self.data.append(
            {'date': date,
             'symbol': symbol,
             'type': transaction_type,
             'amount': amount,
             'price': price}, ignore_index=True)
        logging.info('%s %f units of %s at %f' % (transaction_type, amount, symbol, price))
        self.process_transaction(transaction_type, symbol, price, amount)
        self.clean_null_assets()

    def clean_null_assets(self):
        self.assets = {key: value for key, value in self.assets.items() if value['amount'] != 0}

    def load_cache(self, cache_file: str):
        if os.path.isfile(cache_file):
            self.data = pd.read_csv(cache_file)
            self.data['date'] = pd.to_datetime(self.data['date'])
        else:
            logging.error("failed to load cache")
            return

        self.assets = {}
        for _, row in self.data.iterrows():
            self.process_transaction(row['type'], row['symbol'], row['price'], row['amount'])
        # clean zero amounts
        self.clean_null_assets()

    def amount(self, symbol: str = ''):
        if symbol == '':
            s = 0.0
            for _, value in self.assets.items():
                s += value['amount']
            return s
        if symbol not in self.assets:
            return 0
        return self.assets[symbol]['amount']

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
        total_value = self.balance()
        results = {}
        for asset in self.assets:
            ta = TA(dealer.historical_data[dealer.historical_data.symbol == dealer.get_symbol_ticker(asset[0])])
            pct_change = ta.single_pct_change()
            final_value = asset[1] + asset[1] * pct_change / 100.0
            results[asset[0]] = {
                "change": (pct_change, final_value),
                "max": (ta.max_in_range()[0], ta.max_pct_in_range()[0], ta.max_in_range()[1])
            }
            total_value += final_value - asset[1]
        results['total'] = (total_value, (total_value - self.balance()) / self.balance() * 100.0)
        return results
