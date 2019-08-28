#!/usr/bin/py

from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
import re

with open("index.html", encoding='utf-8') as fp:
    soup = BeautifulSoup(fp.read(), 'html.parser')

rows = soup.find('tbody', id=re.compile(
    "patternTable")).find_all('tr', id=re.compile('row'))

for row in rows:
    fields = row.find_all('td')
    #   1       2       3           4           5       6        7   8
    # 	Name	Symbol	Timeframe	Reliability	Pattern	Candle# 	CandleTime
    print(fields[1].text, fields[2].text, fields[3].text,
          fields[4]['title'], fields[5].text, fields[6].text, fields[8]['title'])
