###############################################################################3
# Download a full day of production trade history of BTC/USD from:
    # Coinbase Pro - https://docs.pro.coinbase.com/
    # Gemini - https://docs.gemini.com/rest-api/
# Store the data in a format of your choice.
#
# Produce a report for each exchange showing:
    # Hourly bars of:
    # Open, high, low, close, change, Volume
# Bonus:
    # Add VWAP per bar
    # Add Notional Value per bar
# Keep your data for further analysis tasks.
#
# Download a full day of production trade history of ETH/BTC from:
    # Coinbase Pro - https://docs.pro.coinbase.com/
# Store the data in a format of your choice.
# Produce a report for for ETH/BTC showing notional volume in USD.
# Make your results, code and data available for review
###############################################################################3
import time
# import cbpro as cbp
import datetime as dt
import pandas as pd
# from cbpro import  public_client
# from coinbasepro import PublicClient,public_client

# import requests, json
import task1
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = "browser"           # super important!! otherwise plotly graphs will not render in IDE (unless using jupyter)

# import csv
# import shutil
# import os
# import coinbasepro as ccoinbasepro


# ## Coinbase Pro BTC-USD
# def pullCoinbase(product_id= 'BTC-USD', granularity=3600):
#     start_time=dt.datetime(2019,11,12)
#     end_time=dt.datetime(2019,11,13)
#     public_client = PublicClient()
#
#     # acceptedGrans = [60, 300, 900, 3600, 21600, 86400]
#     historic_rates = public_client.get_product_historic_rates(product_id = product_id,start=start_time,end=end_time,granularity=granularity)
#
#     dfCoinbase = pd.DataFrame(historic_rates)
#     dfCoinbase.columns = ['time', 'low', 'high', 'open', 'close', 'volume']
#
#     # convert timestamp
#     dfCoinbase['timestamp']=pd.to_datetime(dfCoinbase['time'][0:], unit= 's', origin= 'unix')
#     # dfCoinbase.head()
#
#     # drop last 11-04
#     # dfCoinbase = dfCoinbase.drop([0])
#     # dfCoinbase.head()
#     # split timestamp into date and time
#     # dfCoinbase['timestamp'] = dfCoinbase['time'].dt.time
#
#     # drop time because we are using Nov 4th data only
#     dfCoinbase = dfCoinbase.drop(['time'], axis=1)
#
#     # set index
#     dfCoinbase.set_index(dfCoinbase['timestamp'],drop=True,inplace=True)
#     dfCoinbase = dfCoinbase.drop(['timestamp'],axis=1)
#     print("\nCOINBASE DATA: ",product_id, "\n", dfCoinbase.head())
#
#     return dfCoinbase

## Coinbase data pull
def pullCoinbase(base_url = "https://api.pro.coinbase.com", product_id = 'BTC-USD', granularity=3600):

    # need to give timeframe parameter for 11/04/2019 00:00:00
    # Coinbase uses seconds since Unix Epoch, therefore:
    start_time = 1572825600
    end_time = 1572911999

    response = task1.get(base_url + "/products/" + product_id + "/candles/" +
                            '?start=' + start_time.__str__() + '?end=' + end_time.__str__() + '?granularity=' + granularity.__str__())
    candles = response.json()

    # convert to dfCoinbase
    dfCoinbase = pd.DataFrame(candles)
    dfCoinbase.columns = ['time', 'low', 'high', 'open', 'close', 'volume']

    # convert timestamp from ms to human readable time
    dfCoinbase['timestamp']=pd.to_datetime(dfCoinbase['time'][0:],unit='ms',origin='unix')

    # filter date to Nov 4th only
    dfCoinbase = dfCoinbase.loc[((dfCoinbase['timestamp'] >= '2019-11-04 00:00:00') & (dfCoinbase['timestamp']<='2019-11-05 00:00:00'))]

    # split timestamp into date and time
    # dfGemini['timestamp'] = dfGemini['time'].dt.time
    # print(dfGemini.head())
    # drop time and filter on date to Nov 4th
    # dfGemini = dfGemini.drop(['time'],axis=1)

    # set index to timestamp
    dfCoinbase.set_index(dfCoinbase['timestamp'],drop=True,inplace=True)
    dfCoinbase = dfCoinbase.drop(['time'],axis=1)
    print("\nCOINBASE DATA: ",product_id.upper(), "\n", dfCoinbase.head())
    return dfCoinbase


## Gemini BTC-USD
def pullGemini(base_url = "https://api.gemini.com/v2", ticker = 'btcusd', time_frame= '1hr'):

    # need to give timeframe parameter for 11/04/2019 00:00:00
    # Gemini recommends using milliseconds instead of seconds:
    start_time_ms = 1572825600000     # milliseconds since epoch

    response = task1.get(base_url + "/candles/" + ticker + "/" + time_frame + "?timestamp=" + start_time_ms.__str__())
    candles = response.json()

    # convert to dfCoinbase
    dfGemini = pd.DataFrame(candles)
    dfGemini.columns = ['time', 'open', 'high', 'low', 'close', 'volume']

    # convert timestamp from ms to human readable time
    dfGemini['timestamp']=pd.to_datetime(dfGemini['time'][0:],unit='ms',origin='unix')

    # filter date to Nov 4th only
    dfGemini = dfGemini.loc[((dfGemini['timestamp'] >= '2019-11-04 00:00:00') & (dfGemini['timestamp']<='2019-11-05 00:00:00'))]

    # split timestamp into date and time
    # dfGemini['timestamp'] = dfGemini['time'].dt.time
    # print(dfGemini.head())
    # drop time and filter on date to Nov 4th
    # dfGemini = dfGemini.drop(['time'],axis=1)

    # set index to timestamp
    dfGemini.set_index(dfGemini['timestamp'],drop=True,inplace=True)
    dfGemini = dfGemini.drop(['time'],axis=1)
    print("\nGEMINI DATA: ",ticker.upper(), "\n", dfGemini.head())

    return dfGemini


def plot_OHLC_bars(df, title):
    fig=make_subplots(rows=2,cols=1,subplot_titles = ("OHLC","Volume"))
    fig.add_trace(go.Candlestick(x=df.index,
                    open=df['open'], high=df['high'],
                    low=df['low'], close=df['close']))
    fig.add_trace(go.Bar(x=df.index,y=df['volume']),row=2,col=1)
    fig.update_layout(showlegend= False, xaxis_rangeslider_visible=False, title = title)
    fig.show()
    return


dfCoinbase = pullCoinbase()
dfCoinbase.to_csv('CBASE-btc_usd-20191104.csv',sep=',')          #output to csv

dfGemini = pullGemini()
dfGemini.to_csv('GEM-btc_usd-20191104.csv',sep=',')          #output to csv

dfCoinbase_ethbtc=pullCoinbase(product_id = 'ETH-BTC')      # pull ETH-BTC data from CoinbasePro
dfCoinbase_ethbtc.to_csv('CBASE-eth_btc-20191104.csv',sep=',')          #output to csv


## ETH/BTC Conversion to notional USD value
# create new database for ethbtc conversion purposes
dfConv=dfCoinbase_ethbtc
dfConv=dfConv.drop(['open','high','low'],axis=1)

# calculate the total btc by close * volume of eth/btc
dfConv['total_ethbtc']=dfConv['close']*dfConv['volume']

# notional value = total btc * price of btc at that timestamp (eg 2.03157 * $9,388.42 = $19,073.23)
dfConv['notional_USD'] = dfConv['total_ethbtc'] * dfCoinbase['close']
print("\nETH/BTC Notional Value in $ USD:\n ", round(dfConv['notional_USD'],2))

dfConv.to_csv('eth_btc_notional_USD-20191104.csv',sep=',')
print("\nETH/BTC NOTIONAL VALUE IN $ USD \n ",dfConv.head())

# plot Coinbase open/high/low/close
plot_OHLC_bars(df=dfCoinbase, title="Coinbase BTC/USD Hourly Bars")

# plot Coinbase open/high/low/close
plot_OHLC_bars(df=dfGemini, title="Gemini BTC/USD Hourly Bars")

