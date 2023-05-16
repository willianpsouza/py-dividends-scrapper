#!/usr/bin/env python3

import requests,json,os
import plotly.express as px

''''
    REFERENCES:
     https://plotly.com/python/line-charts/#style-line-plots
     https://statusinvest.com.br/acao/getearnings?IndiceCode=ibovespa&Filter=%20&Start=2021-01-01&End=2022-12-31
     https://statusinvest.com.br/acoes/proventos/ibovespa
     https://plotly.com/python/graphing-multiple-chart-types/
     https://plotly.com/python/
     https://plotly.com/python/basic-charts/
'''

class Shares:
    def __init__(self, ticker, value):
        self.ticker = ticker
        self.value = float(value.replace(",", "."))

    def data(self) -> dict:
        ''' define ticker structure'''
        return {'ticker': self.ticker, 'value': self.value}


def loaddatafromstatusinvest(year: str = "2021") -> dict:
    ''' scraping data from statusinvest api'''
    url: str = "https://statusinvest.com.br/acao/getearnings"
    ini_date: str = f"{year}-01-01"
    end_date: str = f"{year}-12-31"

    parameters: dict = {
        'IndiceCode': 'ibovespa', 
        'Filter': ' ', 
        'Start': ini_date, 
        'End': end_date
    }

    headers: dict = {
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    __url: str = f"data-{year}.json"

    if os.path.isfile(__url):
        _v: dict = loaddatafromfile(year)
    else:
        with requests.get(url, params=parameters, headers=headers, timeout=86400) as _f:
            if _f.status_code == 200:
                _v: str = json.loads(_f.text)
        with open(__url,'w+', encoding='utf-8') as _f:
            _f.writable(_v)
    return _v


def loaddatafromfile(year: str = "2021") -> dict:
    __url: str = f"data-{year}.json".encode('utf-8')
    with open(__url, 'r',encoding='utf-8') as _f:
        __v: dict = json.loads(_f.read())
        return __v


def main(year: str = "2021") -> None:
    FROM: str = 'web'
    t: dict = {}
    if FROM == 'archive':
        __data: dict = loaddatafromfile(year)
    if FROM == 'web':
        __data: dict = loaddatafromstatusinvest(year)
    __dictkey: str = "dateCom"
    for c in __data[__dictkey]:
        p: dict = (Shares(c['code'], c['resultAbsoluteValue']).data())
        if p['ticker'] not in t.keys():
            t[p['ticker']] = {'t_value': p['value'], 't_times': 1}
        else:
            t[p['ticker']]['t_value'] += p['value']
            t[p['ticker']]['t_times'] += 1
    shares: list = []
    times: list = []
    values: list = []
    t = dict(sorted(t.items()))
    for c in t:
        shares.append(c)
        times.append(t[c]['t_times'])
        values.append(t[c]['t_value'])
    fig = px.line(x=shares, y=times, color=px.Constant("Total"), labels=dict(x="Shares", y="Times", color="Values"))
    fig.add_bar(x=shares, y=values, name="Values")

    titulo = f"Dividendos pagos em {year}"
    fig.update_layout(title=titulo,
                      xaxis_title='Numero de vezes que pagou dividendo',
                      yaxis_title='Total de Dividendo Pago')

    fig.show()

    return None

if __name__ == "__main__":
    try:
        year = os.getenv('YEAR', '2011')
        main(year)
    except KeyboardInterrupt:
        pass
