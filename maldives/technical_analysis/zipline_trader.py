from zipline.api import order, record, symbol, set_benchmark
import zipline
from datetime import datetime
import pandas as pd
import pytz
from collections import OrderedDict


def initialize(context):
    set_benchmark(symbol("PETR4"))


def handle_data(contex, data):
    order(symbol("PETR4"), 10)
    record(PETR4=data.current(symbol("PETR4"), "price"))


if __name__ == "__main__":
    data = OrderedDict()
    tickers = ["PETR4"]

    for ticker in tickers:
        data[ticker] = pd.read_csv("../../data/" + ticker + "_yf_data", index_col=0, parse_dates=['Date'])
        data[ticker] = data[ticker][["Open", "High", "Low", "Close", "Adj Close", "Volume"]]

    print(data)

    # perf = zipline.run_algorithm(start=datetime(2020, 3, 5, 0, 0, 0, 0, pytz.utc),
    #                              end=datetime(2021, 3, 5, 0, 0, 0, 0, pytz.utc),
    #                              initialize=initialize,
    #                              capital_base=100000,
    #                              handle_data=handle_data,
    #                              data=data["PETR4"]
    #                              )
