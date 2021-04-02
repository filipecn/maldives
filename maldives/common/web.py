from urllib.request import Request, urlopen


def get_raw_html(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    fp = urlopen(req)
    raw_html = fp.read()  # .decode("utf8")
    fp.close()
    return raw_html
