#!/usr/bin/py
import argparse
import numpy as np
import pandas as pd
from b3_register import B3Register
from technical_analysis import *
import plotly as py
import plotly.graph_objs as go
import cufflinks as cf

if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("file", type=str, help="b3 historical data .txt file")
    args = parse.parse_args()
    columns = []
    registers = []
    with open(args.file, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            b3Register = B3Register(lines[i])
            register = []
            for attribute in b3Register.attributes:
                register.append(b3Register.attributes[attribute])
                if i == 1:
                    columns.append(attribute)
            registers.append(register)
    # use pandas to represent registers data
    data = np.array(registers)
    df = pd.DataFrame(data=data[0:, 0:], columns=columns)
    # get registers from a particular ticket
    ticketRegisters = df[df['negotiationCode'] == 'UGPA3']
    # choose attributes
    attributes = ['closePrice', 'openPrice',
                  'maxPrice', 'minPrice', 'negotiationVolume', 'quoteFactor']
    dates = pd.to_datetime(ticketRegisters['date'])
    quotes = ticketRegisters[attributes]
    for att in attributes:
        quotes.loc[:, att] = pd.to_numeric(quotes[att])
    sup, supIds = computeResistenceLines(quotes.openPrice, quotes.closePrice, 0.01)
    # Calculate the 20 and 100 days moving averages of the closing prices
    short_rolling = quotes.loc[:, 'closePrice'].rolling(window=10).mean()
    long_rolling = quotes.loc[:, 'closePrice'].rolling(window=20).mean()
    # relative returns
    returns = quotes.loc[:, 'closePrice'].pct_change(1)
    log_returns = np.log(quotes.closePrice).diff()
    returns[0] = 0
    log_returns[0] = 0
    relativeReturns = []
    logReturns = []
    for c in range(len(log_returns)):
        logReturns.append(log_returns[c].cumsum()[0])
    for c in range(len(log_returns)):
        relativeReturns.append(100*(np.exp(log_returns[c].cumsum()[0]) - 1))
    # Bollinger bands
    bb_avg, bb_upper, bb_lower = bollingerBands(quotes.loc[:,'closePrice'])
    bbLower = go.Scatter(x=dates, y=bb_upper, yaxis='y2', 
                         line = dict( width = 1 ),
                         marker=dict(color='#ccc'), hoverinfo='none', 
                         legendgroup='Bollinger Bands', name='Bollinger Bands')
    bbUpper =  go.Scatter(x=dates, y=bb_lower, yaxis='y2',
                         line = dict( width = 1 ),
                         marker=dict(color='#ccc'), hoverinfo='none',
                         legendgroup='Bollinger Bands', showlegend=False )
    # volume data
    INCREASING_COLOR = '#17BECF'
    DECREASING_COLOR = '#7F7F7F'
    colors = [DECREASING_COLOR]
    for i in range(1, len(quotes.closePrice)):
        if quotes.closePrice[i] > quotes.closePrice[i-1]:
            colors.append(INCREASING_COLOR)
        else:
            colors.append(DECREASING_COLOR)
    volume = go.Bar(yaxis='y', x=dates, y=quotes.negotiationVolume,
                    marker=dict(color=colors),
                    name='Volume')
    trace = go.Candlestick(name='candles',
                           yaxis='y2',
                           x=dates,
                           open=quotes.openPrice,
                           high=quotes.maxPrice,
                           low=quotes.minPrice,
                           close=quotes.closePrice,
                           increasing=dict(line=dict(color='rgb(32,155,160)')),
                           decreasing=dict(line=dict(color='rgb(253,93,124)')))
    trace_short = go.Scatter(yaxis='y2', x=dates, y=short_rolling,
                             name='SMA10', line=dict(dash='dot'),  hoverinfo = 'none')
    long_short = go.Scatter(yaxis='y2', x=dates, y=long_rolling,
                             name='SMA20', line=dict(dash='dot'),  hoverinfo = 'none')
    relative_returns = go.Scatter(yaxis='y3', x=dates, y=relativeReturns,
                             name='SMA20', line=dict(dash='dot'))
    log_returns = go.Scatter(yaxis='y3', x=dates, y=logReturns,
                             name='SMA20', line=dict(dash='dot'))
    layout = go.Layout(
        title='Double Y Axis Example',
        xaxis=dict(
            rangeselector=dict(
                x=0, y=0.9,
                bgcolor='rgba(150, 200, 250, 0.4)',
                font=dict(size=13),
                buttons=list([
                    dict(count=1,
                         label='reset',
                         step='all'),
                    dict(count=1,
                         label='1yr',
                         step='year',
                         stepmode='backward'),
                    dict(count=3,
                         label='3 mo',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='1 mo',
                         step='month',
                         stepmode='backward'),
                    dict(step='all')
                ])),
        ),
        yaxis=dict(
            title='Negotiation Volume',
            domain = [0, 0.2], 
            showticklabels = False
        ),
        yaxis2=dict(
            title='Price',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            domain = [0.2, 1.0],
            anchor='free',
            # overlaying='y',
            # side='right',
        ),
        yaxis3=dict(
            title='as',
            domain = [0.2, 1.0],
            overlaying='y', 
            # anchor='free',
            side='right',
            hoverformat = '.2f%'
            # showticklabels = False
        ),
        #paper_bgcolor='rgb(44,58,71)',
        #plot_bgcolor='rgb(44,58,71)'
    )

    data = [trace, trace_short, long_short, volume, bbLower, bbUpper, relative_returns]
    for i in range(len(sup)):
        s = sup[i]
        supId = supIds[i]
        if len(s) > 5:
            data.append(go.Scatter(yaxis='y2', x=dates[supId + [len(dates) - 1]], y=(len(supId) + 1) * [np.mean(s)],
                               name='SMA20', line=dict(dash='dot'),  hoverinfo = 'none'))
    fig = go.Figure(data=data, layout=layout)
    py.offline.plot(fig, filename='simple_candlestick')

    # with plt.xkcd():
    # with plt.style.context('Solarize_Light2'):
    #   fig, ax = plt.subplots(figsize=(16,9))
    #    ax.plot(close['date'], close['closePrice'], label='UGPA3')
    #    ax.plot(close['date'], short_rolling, label='20 days rolling')
    #    ax.plot(close['date'], long_rolling, label='100 days rolling')
    #    ax.grid(True)
    #    ax.set_xlabel('Date')
    #    ax.set_ylabel('Adjusted closing price ($)')
    #    ax.legend()
    #    fig.autofmt_xdate()
    # plt.show()
