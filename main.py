from datetime import datetime, timedelta
import time
import os
import pandas as pd
from slackbot import MySlackBot
from upbit import MyUpbit, trade_logic_backtest2


# data = pd.read_csv("ETH-USD.csv")

# portfolio = {'cash': 100000000, 'coins': 0, 'sell_price': 0}

# def current_value(open_value):
#     return portfolio['cash'] + portfolio['coins'] * open_value

# for i in range(len(data)):

#     if i < 120 or i > 300:
#         continue
#     decision = trade_logic_backtest2(data, i)

#     row = data.iloc[i]
#     open_value = row['open']
#     if decision == 'buy' and portfolio['cash'] > 0:
#         target_coins = portfolio['cash']*0.05 / open_value
#         portfolio['coins'] += target_coins
#         portfolio['cash'] = portfolio['cash'] - (target_coins * open_value)
#         portfolio['sell_price'] = open_value
#         print(row['Date'], 'buy', current_value(open_value), portfolio['coins'], portfolio['cash'])
#     elif decision == 'sell' and portfolio['coins'] > 0:
#         target_coins = portfolio['coins'] * 0.5
#         portfolio['cash'] += target_coins * open_value
#         portfolio['coins'] = portfolio['coins'] - target_coins
#         print(row['Date'], 'sell', current_value(open_value), portfolio['coins'], portfolio['cash'])
#     else:
#         print(row['Date'], decision, current_value(open_value), portfolio['coins'], portfolio['cash'])

# portfolio_value = portfolio['cash'] + portfolio['coins'] * data.iloc[-1]['open']
# print('Final portfolio value:', portfolio_value)
# print('Profit:', portfolio_value - 100000000)

# exit()


ACCESS = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
SECRET = os.environ['UPBIT_OPEN_API_SECRET_KEY']

if __name__ == "__main__":
    my_upbit = MyUpbit(ACCESS, SECRET)
    upbit = my_upbit.get_instance()
    slack_bot = MySlackBot()
    slack_bot.send_message('#upbit', '매매 시작합니다.')

    while True:
        now = datetime.now()
        ticker = "KRW-ETH"

        # Run the trading logic once a day
        if now.hour == 0 and now.minute == 0:
            portfolio = my_upbit.get_portfolio()
            [decision, reason] = my_upbit.trade_logic(ticker)
            
            amount = 0
            if decision == 'buy' and portfolio['cash'] > 0:
                amount = portfolio['cash'] * 0.05
                order = upbit.buy_market_order(ticker, amount)

            elif decision == 'sell' and portfolio['coins'] > 0:
                amount = portfolio['coins'] * 0.5
                order = upbit.sell_market_order(ticker, amount)
            print(now, decision, amount, portfolio['cash'], portfolio['coins'])
            slack_bot.send_message('#upbit', f'{now} {decision} {amount}원 {reason}\n현재가치: {portfolio["total"]}\n======\nCash: {portfolio["cash"]}\nETH: {portfolio["coins"]}')
        time.sleep(60)
