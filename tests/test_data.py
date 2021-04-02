import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from maldives.data import fundamentus as fund

if __name__ == '__main__':
    data = fund.get_symbol_list("raw_fund_html", False)
    print(data.head())
