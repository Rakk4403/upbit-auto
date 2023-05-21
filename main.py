from datetime import datetime, timedelta
import time
import os

from upbit import MyUpbit

ACCESS = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
SECRET = os.environ['UPBIT_OPEN_API_SECRET_KEY']


if __name__ == "__main__":
    my_upbit = MyUpbit(ACCESS, SECRET)
    upbit = my_upbit.get_instance()

    while True:
        now = datetime.now()
        ticker = "KRW-ETH"

        # Run the trading logic once a day
        if now.hour == 0 and now.minute == 0:
            portfolio = my_upbit.get_portfolio()
            decision = my_upbit.trade_logic(ticker)
            
            amount = 0
            if decision == 'buy' and portfolio['cash'] > 0:
                amount = portfolio['cash'] * 0.05
                order = upbit.buy_market_order(ticker, amount)

            elif decision == 'sell' and portfolio['coins'] > 0:
                amount = portfolio['coins'] * 0.5
                order = upbit.sell_market_order(ticker, amount)
            print(now, decision, amount, portfolio['cash'], portfolio['coins'])
        time.sleep(60)
