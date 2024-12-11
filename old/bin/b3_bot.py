#!/usr/bin/python3

import importlib
import signal
import sys
import os
import threading
import logging
import datetime
from yahooquery import Ticker

logging.basicConfig(format="%(asctime)s: %(message)s",
                    level=logging.INFO,
                    datefmt="%H:%M:%S")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from maldives.bot.strategies.logger import Logger
from maldives.bot.strategies.mr_little_robot import MrLittleRobot
from maldives.bot.brokers.yq_broker import YQBroker


















# start = datetime.datetime(year=2021, day=4, month=1)



strategy = MrLittleRobot(60 * 60 * 24)
strategy.dealer = YQBroker()
# strategy.dealer.historical_symbol_ticker_candle("petr4", start)
# prices = strategy.dealer.historical_symbol_ticker_candle("petr4", start)
# print(strategy.prices)
strategy.backtrace(datetime.datetime(year=2021, day=20, month=6))









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
