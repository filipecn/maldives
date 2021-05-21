#!/usr/bin/python3
import os
import sys
import logging
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from maldives.bot.exchanges.binance_exchange import BinanceExchange
from maldives.technical_analysis import TA

logging.basicConfig(format="%(asctime)s: %(message)s",
                    level=logging.INFO,
                    datefmt="%H:%M:%S")

with open(sys.argv[1], 'r') as f:
    key = f.readline()[:-1]
    secret = f.readline()[:-1]

exchange = BinanceExchange(key, secret)
exchange.currency = 'BRL'
assets = ['BTC',
          # 'USDT',
          'ETH',
          # 'XRP',
          # 'BUSD',
          # 'BNB',
          # 'DOGE',
          # 'CHZ',
          # 'ADA',
          # 'WIN',
          # 'LTC',
          # 'LINK',
          # 'BTT',
          # 'HOT',
          # 'DOT'
          ]

data = exchange.historical_symbol_ticker_candle(assets, datetime(year=2021, day=27, month=4), None, '1m')

symbols = exchange.get_symbol(assets)
hs = []
for s in symbols:
    hs.append(exchange.historical_data[exchange.historical_data.symbol == s])

plt.style.use('fivethirtyeight')
fig, ax1 = plt.subplots()

for i in range(len(hs)):
    if i == 0:
        ax1.plot(hs[i]['close'].pct_change(1).reset_index(drop=True), linewidth=3, label=assets[i])
    else:
        ax1.plot(hs[i]['close'].pct_change(1).reset_index(drop=True), linewidth=1, label=assets[i])
ax1.legend()

plt.show()
