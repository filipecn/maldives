import pandas as pd
from bs4 import BeautifulSoup
from ..common import web
import re


def get_symbol_list(cache="", update_cache=True):
    """

    :param cache:
    :param update_cache:
    :return:
    """
    url = "https://fundamentus.com.br/detalhes.php?papel="
    raw_html = ""
    if len(cache) > 0 and not update_cache:
        with open(cache, "rb") as f:
            raw_html = f.read()
    else:
        raw_html = web.get_raw_html(url)
        if len(cache) > 0 and update_cache:
            with open(cache, "wb") as f:
                f.write(raw_html)
    soup = BeautifulSoup(raw_html, 'html.parser')
    table = soup.find('table', id=re.compile('test1')).find('tbody').find_all('tr')
    df = pd.DataFrame(columns=['papel', 'nome_comercial', 'razao_social'])
    for tr in table:
        columns = tr.find_all('td')
        df = df.append({'papel': columns[0].find('a').text,
                        'nome_comercial': columns[1].text,
                        'razao_social': columns[2].text
                        }, ignore_index=True)
    return df
