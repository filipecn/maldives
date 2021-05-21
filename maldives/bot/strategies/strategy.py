import threading
import time
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from ..models.price import Price
from ..models.order import Order
from ..models.dealer import Dealer


class Strategy(ABC):
    assets: [str]
    prices: [Price]
    dealer: Dealer

    def __init__(self, interval=60, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.portfolio = {}
        self.asset = ''

    def _run(self):
        self.is_running = False
        self.start()
        self.prices = self.dealer.symbol_ticker(self.assets)
        self.run()

    @abstractmethod
    def run(self):
        pass

    def backtrace(self, start: datetime, end=None, interval='1d'):
        if end is None:
            end = datetime.now()
        prices = self.dealer.historical_symbol_ticker_candle(self.assets, start, end, interval)
        current_index = 0
        while True:
            self.prices = []
            for asset in prices:
                if len(prices[asset]) > current_index:
                    self.prices.append(prices[asset][current_index])
            if len(self.prices) == 0:
                break
            else:
                self.run()
            current_index += 1

    def start(self):
        if not self.is_running:
            if self._timer is None:
                self.next_call = time.time()
            else:
                self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

    def buy(self, **kwargs):
        order = Order(
            symbol=self.dealer.get_symbol(self.asset),
            type=Order.BUY,
            **kwargs
        )
        self.order(order)

    def sell(self, **kwargs):
        order = Order(
            symbol=self.dealer.get_symbol(self.asset),
            type=Order.SELL,
            **kwargs
        )
        self.order(order)

    def order(self, order: Order):
        broker_order = self.dealer.order(order)
        print(broker_order)
