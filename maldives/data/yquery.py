from yahooquery import Ticker


def download(ticker, filename=None, period='1y', interval='1d', start='', end=''):
    """
        https://yahooquery.dpguthrie.com/

    :param ticker: stock symbol
    :param period: valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    :param interval: valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    :param start: YYYY–MM–DD
    :param end: YYYY–MM–DD
    :return:
    """
    ticker = Ticker(ticker + ".SA")

    if len(start) and len(end):
        data = ticker.history(start=start, end=end, interval=interval)
    else:
        data = ticker.history(period=period, interval=interval)
    if filename is not None and len(data):
        data.to_csv(filename)

    return ticker
