from ..strategies.strategy import Strategy
import logging
from datetime import datetime, timedelta
from maldives.technical_analysis import TA
import matplotlib.pyplot as plt
import random
import pandas as pd


class Rands(Strategy):
    def __init__(self, timeout=60):
        super().__init__(timeout)
        self.profit = []
        self.random_state = 2
        self.stop_gain = 1.01
        self.stop_loss = 0.995
        self.buy_time = []
        self.sell_time = []
        self.full_df = pd.DataFrame()

    def prepare_backtrace_instance(self):
        self.profit = []
        self.buy_time = []
        self.sell_time = []

    def prepare_backtrace(self):
        start_date = self.current_time - timedelta(seconds=self.interval)
        logging.info('downloading...')
        prices = self.dealer.historical_candle_series(self.symbols_of_interest, start_date, datetime.now(), '15m')
        self.full_df = prices['BTC']['ta'].data
        logging.info('...done')

    def run(self):
        # jump weekends
        # if self.current_time.isoweekday() > 5:
        #     return

        logging.info('*******************************')
        logging.info('current time: ' + str(self.current_time))

        # retrieve prices

        start_date = self.current_time - timedelta(seconds=self.interval)
        end_date = self.current_time
        logging.info('start: ' + str(start_date) + ' end: ' + str(end_date))

        df = self.full_df.loc[(self.full_df['date'] >= start_date) & (self.full_df['date'] <= end_date)]
        loc = df.sample(n=1)['date'].item()
        df_filtro = df.loc[df['date'] >= loc].reset_index(drop=True)
        logging.info(str(len(df)) + ' ' + str(loc))

        buy_price = df_filtro['close'][0]
        self.buy_time += [df_filtro['date'][0]]
        self.wallet.register(df_filtro['date'][0], 'BTC', 'BUY', buy_price, self.wallet.cash / buy_price)
        for _, row in df_filtro.iterrows():
            current = row['close']
            sell_price = current
            sell_time = row['date']
            if current / buy_price > self.stop_gain:
                sell_price = current
                break
            elif current / buy_price < self.stop_loss:
                sell_price = current
                break
        self.profit += [sell_price / buy_price]
        self.sell_time += [sell_time]
        self.wallet.register(df_filtro['date'][0], 'BTC', 'SELL', sell_price, self.wallet.amount('BTC'))
