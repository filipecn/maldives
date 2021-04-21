import threading
import time
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from ..models.price import Price
from ..models.order import Order
from ..brokers.broker import Broker


class Strategy(ABC):
    price: Price
    broker: Broker

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
        self.set_price(self.broker.symbol_ticker())
        self.run()

    def set_price(self, price):
        self.price = price

    @abstractmethod
    def run(self):
        pass

    def backtrace(self, start: datetime, end=None, interval=60 * 60 * 24):
        self.broker.download_history(start, end)
        if end is None:
            end = datetime.now()
        current_time = start
        while current_time < end:
            # check if date is valid
            price = self.broker.historical_symbol_ticker_candle(current_time)
            if price.date == current_time:
                self.set_price(price)
                self.run()
            current_time += timedelta(seconds=interval)

    def start(self):
        if not self.is_running:
            print(datetime.now())
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
            symbol=self.broker.get_symbol(),
            type=Order.BUY,
            **kwargs
        )
        self.order(order)

    def sell(self, **kwargs):
        order = Order(
            symbol=self.broker.get_symbol(),
            type=Order.SELL,
            **kwargs
        )
        self.order(order)

    def order(self, order: Order):
        broker_order = self.broker.order(order)
        print(broker_order)
