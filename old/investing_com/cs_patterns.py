#!/usr/bin/py
import argparse
import pandas as pd
import numpy as np
import os
from datetime import date
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit

if __name__ == '__main__':
    parse = argparse.ArgumentParser(description="asd")
    parse.add_argument("-input", type=str,
                       help="html file")
    args = parse.parse_args()
    if args.input:
        with open(args.input, encoding='utf-8') as fp:
            soup = BeautifulSoup(fp.read(), 'html.parser')
        rows = soup.find('tbody', id=re.compile(
            "patternTable")).find_all('tr', id=re.compile('row'))
        new_rows = []
        for row in rows:
            fields = row.find_all('td')
            #   1       2       3           4           5       6        7   8           9
            # 	Name	Symbol	Timeframe	Reliability	Pattern	Candle# 	CandleTime   status
            new_rows.append([fields[1].text, fields[2].text, fields[3].text,
                             fields[4]['title'], fields[5].text, fields[6].text, fields[8]['title'],
                             date.today().strftime("%Y-%m-%d"),
                             'wait'])
        new_data = pd.DataFrame(np.array(new_rows), columns=[
            'Name', 'Symbol', 'Timeframe', 'Reliability', 'Pattern', 'Candle', 'CandleTime', 'Date', 'Status'])
        if os.path.isfile('pattern_data.csv') == True:
            data = pd.read_csv('pattern_data.csv', index_col=0)
            data = data.append(new_data)
        data = data.drop_duplicates()
        data.to_csv('pattern_data.csv')
