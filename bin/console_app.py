"""Command-line TA tool

With this tool you can:

    - download/update history data from stock symbols
    - compute TA indicators
"""
import sys
import os
import logging
from yahooquery import Ticker
import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import maldives.data.fundamentus as fund
import maldives.data.yfinance_api as yfc
from maldives.technical_analysis import TA


class TColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def last_resistance_line(values_and_indices, current_index=1000000000):
    lines = values_and_indices[1]
    last_index = max(lines[0])
    last_line = 0
    for i in range(1, len(lines)):
        max_index = max(lines[i])
        if last_index < max_index < current_index:
            last_index = max_index
            last_line = i
    if last_index <= current_index:
        return np.array(values_and_indices[0][last_line]).mean()
    return 0


def run(ta, index, current_price, data):
    support = last_resistance_line(data.support_lines, index)
    support_distance = -(current_price - support) / current_price * 100
    resistance = last_resistance_line(data.resistance_lines, index)
    resistance_distance = (resistance - current_price) / current_price * 100
    print("{:4.2f}  {:4.2f}  {:4.2f}  {:4.2f}  {:4.2f}".format(current_price,
                                                               support, support_distance, resistance,
                                                               resistance_distance))


def plot_ta(ta):
    plt.style.use('fivethirtyeight')

    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.subplots_adjust(hspace=0.5)

    ax1.plot(ta.data['close'], label="Price")
    ax1.plot(ta.sma(10), label="SMA 10")
    ax1.plot(ta.sma(21), label="SMA 21")
    # _, si = ta.resistance_lines("s")
    # line_index = last_resistance_line(si)
    # ax1.plot(len(ta.data) * [ta.data['close'].iloc[si[line_index]].mean()], label="Support Line")
    # _, si = ta.resistance_lines("r")
    # line_index = last_resistance_line(si)
    # ax1.plot(len(ta.data) * [ta.data['close'].iloc[si[line_index]].mean()], label="Resistance Line")
    # plt.plot(ta.ema(10), label="EMA 10")
    # plt.plot(ta.ema(21), label="EMA 21")
    # plt.plot(ta.data.iloc[ta.decimate()]['close'], label="decimate")
    # plt.plot(ta.data.iloc[ta.pips()]['close'], label="pips")
    # m, u, l = ta.bollinger_bands()
    # plt.plot(u, label="Bollinger upper band")
    # plt.plot(l, label="Bollinger lower band")
    print(ta.regional_locals())
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price")
    ax1.legend()

    # ax2.plot(ta.data['volume'], label="Volume")
    # ax2.plot(ta.mac(10, 21)[1], label="MAC 10 21")
    ax2.plot(ta.rsi(), label="RSI")

    plt.show()


if __name__ == "__main__":
    # setup logging
    logging.basicConfig(format="%(asctime)s: %(message)s",
                        level=logging.INFO,
                        datefmt="%H:%M:%S")
    # parse arguments
    parser = argparse.ArgumentParser(description="")
    # retrieve symbol list
    # symbol_list = fund.get_symbol_list("../tests/raw_fund_html", False).sample(1)
    symbol_list = ["PETR4"]
    # create ticker list
    tickers = list()
    for name in symbol_list:
        logging.info("Downloading history of %s", name)
        tickers.append(Ticker(name + ".SA"))
    # retrieve history data
    tas = []
    for ticker in tickers:
        # check cache first
        cache_file = "../data/" + ticker.symbols[0]
        if os.path.isfile(cache_file):
            tas.append(TA(pd.read_csv(cache_file)))
        else:
            data = ticker.history()
            data.to_csv(cache_file)
            tas.append(TA(data))


    class Data:
        resistance_lines = None
        support_lines = None


    for ta in tas:
        data = Data()
        data.support_lines = ta.resistance_lines("s")
        data.resistance_lines = ta.resistance_lines("r")
        ta.run(run, data)

        current_price = ta.data['close'].iloc[-1]
        support = last_resistance_line(ta.resistance_lines('s'))
        support_distance = -(current_price - support) / current_price * 100
        resistance = last_resistance_line(ta.resistance_lines('r'))
        resistance_distance = (resistance - current_price) / current_price * 100
        print("{:4.2f}  {:4.2f}  {:4.2f}  {:4.2f}  {:4.2f}".format(current_price,
                                                                   support, support_distance, resistance,
                                                                   resistance_distance))
        # plot_ta(ta)
    print(symbol_list)
    print(tickers[0].asset_profile)

    exit(0)
    # Informações financeiras
    petr = Ticker("PETR4.SA")
    petr = petr.income_statement()
    petr = petr.transpose()
    petr.columns = petr.iloc[0, :]
    petr = petr.iloc[2:, :-1]
    petr = petr.iloc[:, ::-1]
    print(petr)
