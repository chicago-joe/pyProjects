# ErisX Interview Onsite Tasks
#
# created by Joseph Loss
# loss2@illinois.edu
#
# -------------------------------------------------------------
import datetime
import dateutil.parser
import time
import pandas as pd
import numpy as np
import requests, json


# Task 1 --------------------------
df = pd.read_csv('C://Users//jloss//PyCharmProjects//erisX-cryptotrading-analysis//data//joseph_interview.csv')

df['time'] = pd.to_datetime(df['time'])
df['hour'] = df['time'].dt.hour

dfHrlyTrans = df.copy()
count = []

for i in dfHrlyTrans['hour'].unique():
    tmp = dfHrlyTrans[dfHrlyTrans.hour==i].count()
    count.append(tmp['time'])
print("hourly count: ", count)


# Task 2 ---------------------------
dfOrders = df.copy()
avgQtyPerHour = []

for i in dfOrders['hour'].unique():
    tmp = np.average(dfOrders[dfOrders.hour==i].quantity)
    avgQtyPerHour.append(tmp)
print("Avg Qty per hour: ", avgQtyPerHour)


# Task 3 ---------------------------
# OHLC from Trade Data
dfOHLC = pd.read_csv('C://Users//jloss//PyCharmProjects//erisX-cryptotrading-analysis//data//joseph_interview.csv',
                     index_col = 0,
                     parse_dates = True)
data_price = dfOHLC['price'].resample('60Min').ohlc()
data_price.head()


# Task 4 ---------------------------
# Download full day production trade data and plot ohlc
def pullTrades(base_url = "https://api.pro.coinbase.com/", product_id='BTC-USD', last_trade=80965000):

    response = requests.get(base_url + "/products/" + product_id + "/trades" + "?after=" + last_trade.__str__())
    trades=response.json()

    dfTrades = pd.DataFrame(trades)
    dfTrades.columns = ['time', 'trade_id', 'price', 'size', 'side']
    count = dfTrades['trade_id'][99]

    while True:
        count = count+99

        response = requests.get(base_url + "/products/" + product_id + "/trades" + "?after=" + count.__str__())
        trades=response.json()
        dfTrades = dfTrades.append(trades)

        print("\n NOW PRINTING TRADE_ID: ", count)
        dfTrades.to_csv('C://Users//jloss//PyCharmProjects//erisX-cryptotrading-analysis//data//btcusd_trade_data.csv', mode='a')

        time.sleep(3.3)
    return dfTrades

# pull trade data
pullTrades()


# Task 4.1 ---------------------------
# import trade data csv
dfTrades = pd.read_csv('C://Users//jloss//PyCharmProjects//erisX-cryptotrading-analysis//data//btcusd_trade_data.csv')
dfTrades = dfTrades.dropna()                # data cleaning
dfTrades = dfTrades.drop_duplicates(subset="trade_id")
dfTrades = dfTrades.drop(columns=['Unnamed: 0'])

# convert ISO 8601 format
dfTrades['time'] = pd.to_datetime(dfTrades['time'])
dfTrades=dfTrades.sort_values('trade_id',ascending=True)

dfTrades = dfTrades.set_index(dfTrades['time'],drop=True)

dfTrades=dfTrades.drop(columns=['time'])

# filter for Jan-12 trades only:
dfTrades = dfTrades['2020-01-12']

# convert price to numeric format
dfTrades['price'] = dfTrades.price.astype(float)

hourlyOHLC = dfTrades['price'].resample('60Min').ohlc()
print("\n\nCoinbase BTC-USD Hourly OHLC Bars: \n", hourlyOHLC)


# import mplfinance as mpf
# tmp = dfTrades.copy()

# # group by order side
# market_side = dfTrades.groupby('side')
# buy_side = market_side.get_group('buy')
# sell_side = market_side.get_group('sell')
#
# # buy side indicates a down-tick because the maker was a buy order and their order was removed
# ask_ohlc = pd.DataFrame(sell_side)
# # sell indicates an up-tick
# bid_ohlc = pd.DataFrame(buy_side)
#
# # resample to hourly bars and compute OHLC for both sides
# ask_ohlc = ask_ohlc['price'].resample('60Min').ohlc()
# bid_ohlc = bid_ohlc['price'].resample('60Min').ohlc()
# print(ask_ohlc.head())
# print(bid_ohlc.head())
#
# # concatenate bid and ask OHLC into one table
# bid_ask_ohlc = pd.concat([ask_ohlc, bid_ohlc], axis=1, keys=['Ask', 'Bid'])
# print(bid_ask_ohlc)
#
