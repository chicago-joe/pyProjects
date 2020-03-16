##############################################################
# ErisX Interview Task 1: Cryptocurrency Hourly Bars / Data Pull
#
# created by Joseph Loss
# loss2@illinois.edu
##############################################################
import datetime as dt
import time
import pandas as pd
import numpy as np
import requests, json
from coinbasepro import PublicClient
import plotly.graph_objects as go               # use plotly for OHLC candlestick plots (viewed in browser, see comment on line 30
from plotly.subplots import make_subplots
### keep the following lines or plotly graphs will not be generated in IDE ###
import plotly.io as pio
pio.renderers.default = "browser"


# format cols in dataframe by converting to type 'float64' and rounding to 2 decimals
def format_decimals(df, decimals=2):
    for col in df.columns:
        if df[col].dtype != 'datetime64[ns]':
            df[col] = df[col].astype('float64').round(decimals)
    return df

# calculate hourly percentage change in 'closing' price (technically this is the close price for the hour)
def calc_pctChange(df):
    # for OHLC plotting
    df['pctChg'] = df['close'].sort_index(ascending=True).pct_change()
    return df

def calc_VWAP(df):
    df['VWAP'] = np.cumsum(df['volume'] * (df['high'] + df['low'])/2) / np.cumsum(df['volume'])
    return df

def plot_OHLC_bars(df, title):
    fig=make_subplots(rows=3,cols=1,subplot_titles = ("OHLC","Volume", "% Change in Price"))
    fig.add_trace(go.Candlestick(x=df.index,
                    open=df['open'], high=df['high'],
                    low=df['low'], close=df['close']))

    # add volume bars as subplot
    fig.add_trace(go.Bar(x=df.index,y=df['volume'],
                         texttemplate="%{y:.0}",
                         textposition="auto",
                         marker=dict(color='rgb(0,153,76)',
                                     line=dict(color='rgb(0,153,76)'))),row=2,col=1)
    fig.add_trace(go.Scatter(x=df.index,y=df['pctChg'], mode="lines+markers+text",
                             texttemplate = "%{y:.2%}",
                             textposition="top center",
                             ),row=3,col=1)

    fig.add_trace(go.Bar(x=df.index,y=df['pctChg'][0:]), row=3,col=1)
    fig.update_yaxes(tickformat='%',ticks="inside",row=3)
    fig.update_layout(template="ggplot2",showlegend= False, xaxis_rangeslider_visible=False, title = title)
    fig.show()

# create bar plots for Bonus reports (VWAP and Notional Value in USD)
def make_BONUS_plots(df, title):
    fig=make_subplots(rows=2,cols=1, subplot_titles = ("VWAP", "Notional Value in USD ($ in thousands)"))

    # calculate VWAP using numpy function
    calc_VWAP(df)
    # calculate notional value in USD (closing price * volume)
    df['Notional_Value_USD'] = (df['close'] * df['volume'])/1000
    format_decimals(df, 2)

    # bar plots didn't look good because of scaling; this is much better data visualization
    fig.add_trace(go.Scatter(x=df.index,y=df['VWAP'], mode="lines+markers+text",
                             texttemplate = "%{y:,0.0}",
                             textposition="top center",
                             textfont=dict(
                                     family="sans serif",
                                     size=10.5
                             )
                             ),row=1,col=1)
    fig.add_trace(go.Bar(x=df.index,y=df['Notional_Value_USD'],
                             texttemplate="%{y:,0.1}",
                             textangle = -30,
                             textposition="outside",
                              textfont=dict(
                                      family="sans serif",
                                      size=14,
                                      # color="crimson"
                              )
                         ),row=2,col=1)
    fig.update_layout(template="plotly_white",showlegend= False, xaxis_rangeslider_visible=False, title = title)
    fig.show()


def pullTrades(base_url = "https://api.pro.coinbase.com/", product_id='BTC-USD'):

    # base_url = "https://api.pro.coinbase.com/"
    # product_id='BTC-USD'
    last_trade = 80874987

    response = requests.get(base_url + "/products/" + product_id + "/trades" + "?after=80870000")
    trades=response.json()

    dfTrades = pd.DataFrame(trades)
    dfTrades.columns = ['time', 'trade_id', 'price', 'size', 'side']
    count = dfTrades['trade_id'][99]

    while True:
        count = count+99
        response = requests.get(base_url + "/products/" + product_id + "/trades" + "?after=" + count.__str__())
        trades=response.json()
        dfTrades = dfTrades.append(trades)

        print("\n\n NOW PRINTING TRADE_ID: ", count)
        print(dfTrades,"\n------------------------------")
        # print(dfTrades.tail(),"\n------------------------------")
        time.sleep(4)
    return dfTrades

pullTrades()


## pull data from Coinbase Pro API
def pullCoinbase(product_id= 'BTC-USD', granularity=3600):
    # acceptedGrans = [60, 300, 900, 3600, 21600, 86400]
    start_time=dt.datetime(2019,11,4)
    end_time=dt.datetime(2019,11,5)

    public_client = PublicClient()
    historic_rates = public_client.get_product_historic_rates(product_id = product_id,
                                                              start = start_time,
                                                              stop = end_time,
                                                              granularity = granularity)
    dfCoinbase = pd.DataFrame(historic_rates)
    dfCoinbase.columns = ['time', 'low', 'high', 'open', 'close', 'volume']

    # convert timestamp
    dfCoinbase['timestamp']=pd.to_datetime(dfCoinbase['time'][0:], unit= 's', origin= 'unix')
    # drop time because we are using Nov 4th data only
    dfCoinbase = dfCoinbase.drop(['time'], axis=1)

    # set index
    dfCoinbase.set_index(dfCoinbase['timestamp'],drop=True,inplace=True)
    dfCoinbase = dfCoinbase.drop(['timestamp'],axis=1)

    print("\nCOINBASE DATA: ", product_id, "\n", dfCoinbase.head())
    return dfCoinbase

## pull data from Gemini API
def pullGemini(base_url = "https://api.gemini.com/v2", ticker = 'btcusd', time_frame= '1hr'):

    # Gemini recommends using milliseconds instead of seconds (since Epoch):
    start_time_ms = 1577944800 * 1000     # ms since Epoch for datetime = 01/02/2020 00:00:00 Local Time (GMT -06:00)
    response = requests.get(base_url + "/candles/" + ticker + "/" + time_frame + "?timestamp=" + start_time_ms.__str__())
    candles = response.json()

    # convert to dfCoinbase
    dfGemini = pd.DataFrame(candles)
    dfGemini.columns = ['time', 'open', 'high', 'low', 'close', 'volume']

    # convert timestamp from ms to human readable time
    dfGemini['timestamp']=pd.to_datetime(dfGemini['time'][0:],unit='ms',origin='unix')

    # filter date to Nov 4th only
    dfGemini = dfGemini.loc[((dfGemini['timestamp'] >= '2019-11-04 00:00:00') & (dfGemini['timestamp']<='2019-11-05 00:00:00'))]

    # set index to timestamp
    dfGemini.set_index(dfGemini['timestamp'], drop=True, inplace=True)
    dfGemini = dfGemini.drop(['time', 'timestamp'], axis=1)

    # calculate hourly percentage change in 'closing' price (technically this is the close price for the hour)
    # dfGemini['pctChg'] = dfGemini['close'].sort_index(ascending=True).pct_change()
    print("\nGEMINI DATA: ",ticker.upper(), "\n", dfGemini.head())
    return dfGemini

dfCoinbase = pullCoinbase()
format_decimals(dfCoinbase, 2)
calc_pctChange(dfCoinbase)              # calculate hourly percentage change in price

dfGemini = pullGemini()
format_decimals(dfGemini, 2)
calc_pctChange(dfGemini)

dfCoinbase_ethbtc=pullCoinbase(product_id = 'ETH-BTC')          # pull ETH-BTC data from CoinbasePro
format_decimals(dfCoinbase_ethbtc, 4)


### Convert ETH/BTC to notional value in $ USD:
dfConv = dfCoinbase_ethbtc                          # create new database for ethbtc conversion purposes
dfConv = dfConv.drop(['open','high','low'],axis=1)      # drop unnecessary

# calculate the total amount in btc = (eth/btc closing price * volume(
dfConv['total_ethbtc'] = dfConv['close']*dfConv['volume']

# notional value = total btc * price of btc at that timestamp (eg 2.03157 * $9,388.42 = $19,073.23)
dfConv['notional_USD'] = dfConv['total_ethbtc'] * dfCoinbase['close']
format_decimals(dfConv, 4)

print("\nETH/BTC Notional Value in $ USD:\n ", dfConv['notional_USD'])
print("\nETH/BTC NOTIONAL VALUE IN $ USD \n ",dfConv.head())
dfConv.to_csv('ETH-BTC Notional Value in USD - 20191104.csv',sep=',')
# timestamps = dfCoinbase.index

## plot Coinbase hourly bars
plot_OHLC_bars(df=dfCoinbase, title="Coinbase BTC/USD Hourly Bars")
# plot Gemini hourly bars
plot_OHLC_bars(df=dfGemini, title="Gemini BTC/USD Hourly Bars")

##  make VWAP and notional value plots to complete bonus tasks
make_BONUS_plots(dfCoinbase, title = "Coinbase BONUS Report")
make_BONUS_plots(dfGemini, title = "Gemini BONUS Report")

# output data to csv
# dfCoinbase_ethbtc.to_csv('CBASE-eth_btc-20191104.csv', sep=',')
dfCoinbase = dfCoinbase.drop(['pctChg'], axis=1)
dfCoinbase.to_csv('Coinbase BTC-USD Hourly Bars - 20191104.csv', sep=',')         # output to csv
dfGemini = dfGemini.drop(['pctChg'], axis=1)
dfGemini.to_csv('Gemini BTC-USD Hourly Bars - 20191104.csv', sep=',')             # output to csv
