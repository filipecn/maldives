#!/usr/bin/py
import argparse
import pandas as pd
from datetime import date


if __name__ == '__main__':
    parse = argparse.ArgumentParser(description="asd")
    parse.add_argument("-patterns", type=str,
                       help="csv file containing patterns")
    parse.add_argument("--data", type=str,
                       help="folder containing stock data")
    parse.add_argument("--profit", type=float,
                       help='expected profit percentage')
    args = parse.parse_args()
    expected_profit = 3.0
    if args.profit:
        expected_profit = args.profit
    pattern_data = pd.read_csv(args.patterns, index_col=0)
    # check each pattern against stock data
    for row in pattern_data.itertuples():
        print('checking "' + row.Pattern + '" pattern for',
              row.Symbol, '(' + row.Date + ')')
        # load stock data
        stock_data = pd.read_csv(row.Symbol + '_stock_data.csv', index_col=0)
        stock_data = stock_data.sort_values(by='date', ascending=True)
        base_value = float(stock_data['4. close'].loc[row.Date])
        # iterate over days while condition is not fulfilled
        daily_data = stock_data.loc[row.Date:]
        day_count = 0
        profit = 0
        for day_row in daily_data.itertuples():
            day_value = float(day_row._4)
            profit = ((day_value - base_value) / base_value) * 100.0
            if day_count > 0 and profit >= expected_profit:
                break
            day_count += 1
        print('\t%.2f%% after %d days.' % (profit, day_count))
