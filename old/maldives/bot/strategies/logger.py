from ..strategies.strategy import Strategy
import logging
from datetime import datetime


class Logger(Strategy):
    def __init__(self, timeout=60):
        super().__init__(timeout)

    def run(self):
        logging.info('*******************************')
        logging.info(self.current_time)
        self.wallet.log()
        # for price in self.prices:
        #     logging.info('symbol: %s', price.symbol)
        #     logging.info('date: %s', price.date)
        #     logging.info('current: %f', price.current)
        #     logging.info('open: %f', price.open)
        #     logging.info('close: %f', price.close)
        #     logging.info('low: %f', price.low)
        #     logging.info('high: %f', price.high)
        #     logging.info('volume: %d', price.volume)
        #     logging.info('interval: %s', price.interval)
        #     logging.info('-----------------------------')
