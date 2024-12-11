from pandas_datareader import data as pdr
import yfinance as yf


def download(ticker, filename=None, period='1y', interval='1d', start='', end=''):
    """

    :param ticker: stock symbol
    :param period: valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    :param interval: valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    :param start:
    :param end:
    :return:
    """
    yf.pdr_override()
    if len(start) and len(end):
        data = pdr.get_data_yahoo(ticker + ".sa", interval=interval, start=start, end=end)
    else:
        data = pdr.get_data_yahoo(ticker + ".sa", period=period, interval=interval)
    if filename is not None:
        data.to_csv(filename)
    return data
