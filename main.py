import pyupbit
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time
import os

ACCESS = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
SECRET = os.environ['UPBIT_OPEN_API_SECRET_KEY']

upbit = pyupbit.Upbit(ACCESS, SECRET)


def calculate_slope(series, degree=1):
    #if series.isnull().any():
    #    return np.nan
    return np.polyfit(range(len(series.dropna())), series.dropna(), degree)[0]


def calculate_atr(high, low, close, n=14):
    hl = high - low
    hc = np.abs(high - close.shift())
    lc = np.abs(low - close.shift())
    tr = pd.DataFrame({'hl': hl, 'hc': hc, 'lc': lc}).max(axis=1)
    return tr.rolling(n).mean()

def trade_logic(ticker):
    data = pyupbit.get_ohlcv(ticker, interval="day", count=120)

    open_value = data['open']
    close = data['close']
    high = data['high']
    low = data['low']

    ma5 = close.rolling(5).mean()
    ma10 = close.rolling(10).mean()
    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()
    ma120 = close.rolling(120).mean()

    atr = calculate_atr(high, low, close)
    todays_range = np.abs(open_value[-1] - close[-1])
    
    slopes = [calculate_slope(ma) for ma in [ma5, ma10, ma20, ma60, ma120]]
    up_trend_count = len([s for s in slopes if s > 0])
    
    # Sell Logic
    if up_trend_count < 3 and (todays_range > atr[-1] or (close[-1] < get_latest_high() * 0.95)):
        return 'sell'
    
    # Buy Logic
    set_latest_high(close[-1])
    if up_trend_count >= 3 and todays_range < atr[-1]:
        return 'buy'
    
    return 'hold'


latest_high = 0

def get_latest_high():
    return latest_high

def set_latest_high(price):
    # set latest_high to price if price is greater than latest_high
    global latest_high
    latest_high = price

def trade_logic_backtest2(data, i):
    close = data['close'].iloc[:i+1]
    high = data['high'].iloc[:i+1]
    low = data['low'].iloc[:i+1]
    open_today = data['open'].iloc[i]
    
    ma5 = close.rolling(5).mean()
    ma10 = close.rolling(10).mean()
    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()
    ma120 = close.rolling(120).mean()

    atr = calculate_atr(high, low, close)
    
    # Change from 'today's high - low' to 'previous day's high - low'
    if i > 0:
        high_yesterday = data['open'].iloc[-1]
        low_yesterday = data['close'].iloc[-1]
        yesterdays_range = high_yesterday - low_yesterday
    else:
        yesterdays_range = np.nan
    
    slopes = [calculate_slope(ma.dropna()) for ma in [ma5, ma10, ma20, ma60, ma120]]
    up_trend_count = len([s for s in slopes if s > 0])
    
    # Sell Logic
    if (up_trend_count < 3 and yesterdays_range > atr.iloc[-1]): # or (close.iloc[-1] < get_latest_high() * 0.50):
        return 'sell'
    
    set_latest_high(close.iloc[-1])
    # Buy Logic
    if up_trend_count >= 3 and yesterdays_range < atr.iloc[-1]:
        
        return 'buy'
    
    return 'hold'


# data = pd.read_csv("ETH-USD.csv")

# portfolio = {'cash': 100000000, 'coins': 0, 'sell_price': 0}

# for i in range(len(data)):
    
#     if i < 120:
#         continue
#     decision = trade_logic_backtest2(data, i)

#     row = data.iloc[i]
#     open_value = row['open']
#     if decision == 'buy' and portfolio['cash'] > 0:
#         target_coins = portfolio['cash']*0.1 / open_value
#         portfolio['coins'] += target_coins
#         portfolio['cash'] = portfolio['cash'] - (target_coins * open_value)
#         portfolio['sell_price'] = open_value
#         print(row['Date'], 'buy', portfolio['coins'], portfolio['cash'])
#     elif decision == 'sell' and portfolio['coins'] > 0:
#         target_coins = portfolio['coins'] * 0.5
#         portfolio['cash'] += target_coins * open_value
#         portfolio['coins'] = portfolio['coins'] - target_coins
#         print(row['Date'], 'sell', portfolio['coins'], portfolio['cash'])
#     else:
#         print(row['Date'], decision, portfolio['coins'], portfolio['cash'])

# portfolio_value = portfolio['cash'] + portfolio['coins'] * data.iloc[-1]['open']
# print('Final portfolio value:', portfolio_value)
# print('Profit:', portfolio_value - 100000000)

def get_portfolio():
    portfolio = {'cash': 0, 'coins': 0}
    portfolio['cash'] = upbit.get_balance('KRW')
    portfolio['coins'] = upbit.get_balance('KRW-ETH')
    return portfolio



if __name__ == "__main__":
    while True:
        now = datetime.now()
        ticker = "KRW-ETH"

        # Run the trading logic once a day
        if now.hour == 0 and now.minute == 0:
            portfolio = get_portfolio()
            decision = trade_logic(ticker)
            
            amount = 0
            if decision == 'buy' and portfolio['cash'] > 0:
                amount = portfolio['cash'] * 0.05
                order = pyupbit.buy_market_order(ticker, amount)

            elif decision == 'sell' and portfolio['coins'] > 0:
                amount = portfolio['coins'] * 0.5
                order = pyupbit.sell_market_order(ticker, amount)
            print(now, decision, amount, portfolio['cash'], portfolio['coins'])
        time.sleep(60)

