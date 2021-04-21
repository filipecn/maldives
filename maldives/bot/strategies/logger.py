from ..strategies.strategy import Strategy
import logging


class Logger(Strategy):
    def __init__(self, timeout=60, *args, **kwargs):
        super().__init__(timeout, *args, **kwargs)

    def run(self):
        logging.info('*******************************')
        logging.info('date: %s', self.price.date)
        logging.info('current: %f', self.price.current)
        logging.info('open: %f', self.price.open)
        logging.info('close: %f', self.price.close)
        logging.info('low: %f', self.price.low)
        logging.info('high: %f', self.price.high)
        logging.info('volume: %d', self.price.volume)
        logging.info('*******************************')

