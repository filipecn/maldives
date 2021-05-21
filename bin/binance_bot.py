#!/usr/bin/python3

import importlib
import signal
import sys
import os
import threading
import logging
import datetime

logging.basicConfig(format="%(asctime)s: %(message)s",
                    level=logging.INFO,
                    datefmt="%H:%M:%S")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from maldives.bot.strategies.logger import Logger
from maldives.bot.exchanges.binance_exchange import BinanceExchange

with open(sys.argv[1], 'r') as f:
    key = f.readline()[:-1]
    secret = f.readline()[:-1]

strategy = Logger()
strategy.assets = ['BTC']
strategy.dealer = BinanceExchange(key, secret)
strategy.dealer.currency = 'BRL'
strategy.backtrace(datetime.datetime(year=2021, day=1, month=1))

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
