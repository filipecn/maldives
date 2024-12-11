#!/usr/bin/python3

import importlib
import signal
import sys
import os
import threading
import logging
import datetime
import pandas as pd

logging.basicConfig(format="%(asctime)s: %(message)s",
                    level=logging.INFO,
                    datefmt="%H:%M:%S")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from maldives.bot.strategies.logger import Logger
from maldives.bot.exchanges.binance_exchange import BinanceExchange
from maldives.bot.strategies.mr_little_robot import MrLittleRobot
from maldives.bot.strategies.rands import Rands

with open(sys.argv[1], 'r') as f:
    key = f.readline()[:-1]
    secret = f.readline()[:-1]

# key =
# secret = ''

# strategy = Logger(60 * 60 * 24)
strategy = MrLittleRobot(60 * 60 * 4)
strategy.wallet.cash = 100
strategy.symbols_of_interest = ['BTC', 'ETH']
strategy.dealer = BinanceExchange(key, secret)
strategy.dealer.currency = 'BRL'

# strategy.dealer.historical_candle_series(['BTC', 'ETH'], datetime.datetime(year=2021, day=1, month=1),
#                                          datetime.datetime(year=2021, day=3, month=1), '15m')

strategy.backtrace(datetime.datetime(year=2021, day=1, month=6))
exit(0)

bootstrap = pd.DataFrame()

for i in range(1):
    strategy.profit = []
    strategy.sell_time = []
    strategy.buy_time = []
    strategy.backtrace(datetime.datetime(year=2021, day=29, month=6),
                       datetime.datetime(year=2021, day=30, month=6))
    total = 1
    for p in strategy.profit:
        total *= p
    bootstrap = bootstrap.append({
        'profit': total
    }, ignore_index=True)

bootstrap.to_csv('bootstrap.csv')

strategy.wallet.log()
print(bootstrap['profit'].describe())

sys.exit(0)

# start bot
strategy.start()


def signal_handler(signal, frame):
    print('stopping strategy...')
    strategy.stop()
    sys.exit(0)


# Listen for keyboard interrupt event
signal.signal(signal.SIGINT, signal_handler)
forever = threading.Event()
forever.wait()
strategy.stop()
sys.exit(0)
