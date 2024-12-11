#!/usr/bin/py
import argparse
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
from datetime import date

if __name__ == '__main__':
    parse = argparse.ArgumentParser(description="asd")
    parse.add_argument("--input", type=str,
                       help="csv file containing pattern data")
    parse.add_argument("--symbol", type=str,
                       help="stock symbol (ex: PETR4)")
    parse.add_argument("--output", type=str,
                       help="csv file containing stock data")
    parse.add_argument("--key", type=str,
                       help="csv file containing stock data")
    args = parse.parse_args()
    ts = TimeSeries(key='YOUR_API_KEY', output_format='pandas')
    symbols = []
    if args.symbol:
        symbols.append(args.symbol)
    elif args.input:
        pattern_data = pd.read_csv(args.input, index_col=0)
        symbols.extend(pattern_data['Symbol'].drop_duplicates())
    for s in symbols:
        print("Downloading " + s + " data ... ")
        s_data, meta_data = ts.get_daily(
            symbol=s + '.SAO', outputsize='compact')
        s_data['Symbol'] = s
        print("\t" + str(s_data.size) + " days retrieved.")
        f = open(args.output "w+")
        f.write(data.to_csv(index=True))
        f.close()
    exit()

    today = date.today()
    print(today.strftime("%Y-%m-%d"))
    print(data.loc[:'2019-08-23', '1. open'])
    # data['4. close'].plot()
    # plt.title('Intraday TimeSeries Google')
    # plt.show()
    if args.output:
        f = open(args.output, "w+")
        f.write(data.to_csv(index=True))
        f.close()
