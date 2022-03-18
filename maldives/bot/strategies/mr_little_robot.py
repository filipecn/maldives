from ..strategies.strategy import Strategy
import logging
from datetime import datetime, timedelta
from maldives.technical_analysis import TA
import matplotlib.pyplot as plt
import random
import pandas as pd


class MrLittleRobot(Strategy):
    def __init__(self, timeout=60):
        super().__init__(timeout)

    def prepare_backtrace_instance(self):
        pass

    def prepare_backtrace(self):
        start_date = self.current_time - timedelta(days=1)
        end_date = datetime(year=2021, month=6, day=30)
        self.dealer.historical_candle_series(self.symbols_of_interest, start_date, end_date, '15m')

    def run(self):
        logging.info('*******************************')
        logging.info('current time: ' + str(self.current_time))
        # history range
        start_date = self.current_time - timedelta(days=7)
        end_date = self.current_time
        for symbol in self.symbols_of_interest:
            logging.info("processing symbol %s" % symbol)

            plt.style.use('fivethirtyeight')
            # fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
            fig, ax1 = plt.subplots()
            ax1.grid(True)

            prices = self.dealer.historical_candle_series(symbol, start_date, end_date, '15m')
            ta: TA = prices[symbol]['ta']

            current_price = float(self.dealer.symbol_ticker(['BTC'])[0].current)

            resistance_levels = ta.resistance_lines_for_price(current_price, 0, 0.01)
            support_levels = ta.support_lines_for_price(current_price, 0, 0.01)

            ax1.plot(len(ta.data['close']) * [current_price], label='current price', linestyle="", marker='o')

            for i in range(len(resistance_levels)):
                label = ((resistance_levels[i][0] - current_price) / current_price) * 100.0
                ax1.plot([resistance_levels[i][2], len(ta.data['close'])], 2 * [resistance_levels[i][0]],
                         label='%.2f%% %d' % (label, resistance_levels[i][1]))
                if i > 3:
                    break
            for i in range(len(support_levels)):
                label = ((current_price - support_levels[i][0]) / current_price) * 100.0
                ax1.plot([support_levels[i][2], len(ta.data['close'])], 2 * [support_levels[i][0]],
                         label='%.2f%% %d' % (label, support_levels[i][1]))
                if i > 3:
                    break

            # ax1.plot(ta.sma(99), label='sma99')
            # ax1.plot(ta.sma(25), label='sma25')
            # ax1.plot(ta.sma(7), label='sma7')
            # ax1.plot(ta.data['close'], label='CLOSE')
            ax1.plot(ta.data['open'], label='OPEN')
            # ax1.plot(ta.decimate(1))
            # ax1.plot(ta.data['close'], label='close', linestyle="", marker="v", markersize=20)
            # ax1.plot(ta.data['open'], label='open', linestyle="", marker="o", markersize=20)
            # ax2.plot(ta.candle_directions(), label='directions', linestyle="", marker="v", markersize=20)
            # ax2.plot(ta.reversals(), label='reversals', linestyle="", marker="o", markersize=20)
            ax1.legend()
            # ax2.legend()

            # symbol_data['prices']

            # logging.info("candle count" + str(len(symbol_data['prices'])))
            # price = symbol_data['prices'][0]
            # logging.info('symbol: %s', price.symbol)
            # logging.info('date: %s', price.date)
            # logging.info('current: %f', price.current)
            # logging.info('open: %f', price.open)
            # logging.info('close: %f', price.close)
            # logging.info('low: %f', price.low)
            # logging.info('high: %f', price.high)
            # logging.info('volume: %d', price.volume)
            # logging.info('interval: %s', price.interval)
            # logging.info('-----------------------------')
            plt.show()

        exit(0)
