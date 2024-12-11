import threading
import time
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from ..models.price import Price
from ..models.order import Order
from ..models.dealer import Dealer
from ..models.wallet import Wallet


class Strategy(ABC):
    money: float
    wallet: Wallet
    dealer: Dealer
    iteration_number: int
    symbols_of_interest: []

    def __init__(self, interval: int):
        self.wallet = Wallet()
        self.interval = interval
        self._timer = None
        self.is_running = False
        self.next_call = time.time()
        self.money = 0.0
        self.iteration_number = 0
        self.current_time = datetime.now()
        # backtrace variables
        self.running_backtrace = False
        self.symbols_of_interest = []
        self.prepared_backtrace = False
        self.jump_weekends = False

    def _run(self):
        self.is_running = False
        self.start()
        self.run()

    @abstractmethod
    def prepare_backtrace(self):
        pass

    @abstractmethod
    def prepare_backtrace_instance(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def backtrace(self, start: datetime, end=None):
        self.running_backtrace = True
        if end is None:
            end = datetime.now()
        self.current_time = start
        if not self.prepared_backtrace:
            self.prepare_backtrace()
            self.prepared_backtrace = True
        while self.current_time < end:
            self.current_time += timedelta(seconds=self.interval)
            if self.jump_weekends and self.current_time.isoweekday() > 5:
                continue
            self.run()
            self.iteration_number += 1
        self.running_backtrace = False

    def bootstrap(self, iterations: int, start: datetime, end=None):
        for i in range(iterations):
            self.prepare_backtrace_instance()
            self.backtrace(start, end)

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
            symbol=self.dealer.get_symbol_ticker(self.asset),
            type=Order.BUY,
            **kwargs
        )
        self.order(order)

    def sell(self, **kwargs):
        order = Order(
            symbol=self.dealer.get_symbol_ticker(self.asset),
            type=Order.SELL,
            **kwargs
        )
        self.order(order)

    def order(self, order: Order):
        broker_order = self.dealer.order(order)
        print(broker_order)
