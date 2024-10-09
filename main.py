import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import yfinance as yf
from binance.spot import Spot
from ta.momentum import StochRSIIndicator, rsi, williams_r
from ta.volatility import BollingerBands
from ta.trend import MACD, trix, cci, adx

from long_buy_strategy import check_long_buy

# PAIRS = ["JPY=X", "GBPUSD=X", "AUDUSD=X", "NZDUSD=X", "EURJPY=X", "GBPJPY=X", "EURGBP=X", "EURCAD=X", "EURSEK=X",
#          "EURCHF=X",
#          "EURHUF=X", "EURJPY=X", "CNY=X", "HKD=X", "SGD=X", "INR=X", "MXN=X", "PHP=X", "IDR=X", "THB=X", "MYR=X",
#          "ZAR=X", "RUB=X"]
# PAIRS = ["BTC-USD", "ETH-USD", "USDT-USD", "BNB-USD", "USDC-USD", "XRP-USD", "STETH-USD", "ADA-USD", "DOGE-USD",
#          "FGC-USD", "WTRX-USD", "SOL-USD", "LTC-USD", "TRX-USD", "DOT-USD", "MATIC-USD"]
NUM_DAYS = 20  # The number of days of historical data to retrieve
INTERVAL = "1h"
PAIRS = ["BTCUSDT", "SOLUSDT", "FTTBUSD", "SHIBUSDT", "XRPUSDT", "DOGEUSDT", "MATICUSDT", "ADAUSDT"]
# "BTCUSDT", "SOLUSDT", "FTTBUSD", "SHIBUSDT", "XRPUSDT", "DOGEUSDT"


def get_binance_data(currency_pair):
    client = Spot()
    candles = client.klines(currency_pair, INTERVAL, limit=1000)
    data_container = []
    datas = []
    for candle in candles:
        data = {
            "Datetime": datetime.datetime.fromtimestamp(candle[6] / 1000),
            "Open": float(candle[1]),
            "High": float(candle[2]),
            "Low": float(candle[3]),
            "Close": float(candle[4]),
        }
        data_container.append(data)
    datas = data_container

    for _ in range(NUM_DAYS):
        data_container = []
        candles = client.klines(currency_pair, INTERVAL, limit=1000, endTime=candles[0][6] - 60000)
        for candle in candles:
            data = {
                "Datetime": datetime.datetime.fromtimestamp(candle[6] / 1000),
                "Open": float(candle[1]),
                "High": float(candle[2]),
                "Low": float(candle[3]),
                "Close": float(candle[4]),
            }
            data_container.append(data)
        data_container.extend(datas)
        datas = data_container

    dataframe = pd.DataFrame().from_dict(datas)
    return dataframe


def get_indicators(dataframe):
    # BOLLINGER BANDS INDICATOR
    bb = BollingerBands(close=dataframe["Close"], window=30)
    bb_hband = bb.bollinger_hband()
    bb_lband = bb.bollinger_lband()
    bb_mband = bb.bollinger_mavg()

    # STOCHRSI INDICATOR STOCH LENGTH 10 UPPER_LIMIT = 100 LOWER_LIMIT = 0
    stochrsi_1 = StochRSIIndicator(close=dataframe["Close"], window=10)
    stochrsi_1_d = stochrsi_1.stochrsi_d()
    stochrsi_1_k = stochrsi_1.stochrsi_k()

    # RSI INDICATOR UPPER_LIMIT = 70 LOWER_LIMIT = 30
    rsi_ind = rsi(close=dataframe["Close"], window=13)

    # STOCHRSI INDICATOR DEFAULT SETTINGS UPPER_LIMIT = 90 LOWER_LIMIT = 10
    stochrsi_2 = StochRSIIndicator(close=dataframe["Close"])
    stochrsi_2_d = stochrsi_2.stochrsi_d()
    stochrsi_2_k = stochrsi_2.stochrsi_k()

    # TRIX INDICATOR
    trix_ind = trix(close=dataframe["Close"], window=18)

    # CCI INDICATOR UPPER_LIMIT = 90 LOWER_LIMIT = -90
    cci_ind = cci(high=dataframe["High"], low=dataframe["Low"], close=dataframe["Close"])

    # MACD INDICATOR
    macd_indicator = MACD(close=dataframe["Close"])
    macd_macd = macd_indicator.macd()
    macd_signal = macd_indicator.macd_signal()

    # %R INDICATOR UPPER_RANGE(0, -20) LOWER_RANGE(-70, -90)
    will_r = williams_r(high=dataframe["High"], low=dataframe["Low"], close=dataframe["Close"], lbp=10)

    # ADX INDICATOR
    adx_ind = adx(high=dataframe["High"], low=dataframe["Low"], close=dataframe["Close"])

    # DATAFRAME WITH EVERY INDICATOR DATA
    indicator_data = pd.DataFrame()
    indicator_data["Bollinger Band High"] = bb_hband
    indicator_data["Bollinger Band Avg"] = bb_mband
    indicator_data["Bollinger Band Low"] = bb_lband
    indicator_data["Stochastics RSI 1 D"] = stochrsi_1_d
    indicator_data["Stochastics RSI 1 K"] = stochrsi_1_k
    indicator_data["RSI"] = rsi_ind
    indicator_data["Stochastics RSI 2 D"] = stochrsi_2_d
    indicator_data["Stochastics RSI 2 K"] = stochrsi_2_k
    indicator_data["TRIX"] = trix_ind
    indicator_data["CCI"] = cci_ind
    indicator_data["MACD IND"] = macd_macd
    indicator_data["MACD SIGNAL"] = macd_signal
    indicator_data["Williams RSI"] = will_r
    indicator_data["ADX"] = adx_ind

    return indicator_data


profit = 0
loss = 0
total_profit = 0
wallet = 1000
for pair in PAIRS:
    pair_profit = 0
    pair_loss = 0
    # df = get_binance_data(pair)
    # df = df.dropna()
    # df.to_csv(f"data_{pair}.csv")
    df = pd.read_csv(f"data_{pair}.csv")
    indicators = get_indicators(df)

    buy_orders = pd.DataFrame()
    length = len(df)
    last_10_candles = []
    last_10_indicators = []
    orders = []
    open_order = False
    for i in range(length - 9):
        last_10_candles = df.iloc[i: i + 10]
        last_10_indicators = indicators.iloc[i: i + 10]

        latest_candle = last_10_candles.iloc[-1]
        latest_indicator = last_10_indicators.iloc[-1]

        if open_order:
            order = orders[-1]
            if latest_candle["High"] > order["Target"]:
                order["Profit"] = True
                open_order = False
                take_profit = order["Amount"] * order["Target"] - wallet
                wallet += take_profit
            elif latest_candle["Low"] < order["Stop Loss"]:
                order["Profit"] = False
                open_order = False
                take_loss = order["Amount"] * order["Stop Loss"] - wallet
                wallet += take_loss

        if check_long_buy(last_10_candles, last_10_indicators) and not open_order:
            open_order = True
            close_price = latest_candle["Close"]
            target = close_price * 1.01
            stop_loss = close_price - (close_price * 0.005)
            # loss_ratio = (1000 / close_price * target - 1000) / 2 * -1
            # stop_loss = (loss_ratio + 1000) / (1000 / close_price)
            new_order = {
                "Datetime": latest_candle["Datetime"],
                "Close": close_price,
                "Target": target,
                "Stop Loss": stop_loss,
                "Profit": False,
                "Amount": wallet / close_price
            }
            orders.append(new_order)

    for order in orders:
        if order["Profit"]:
            profit += 1
            pair_profit += 1
        elif not order["Profit"]:
            loss += 1
            pair_loss += 1

    temp = pd.DataFrame(orders)
    temp.to_csv(f"test_{pair}.csv")

    print(f"PAIR[{pair}] Profit/Loss Ratio: {pair_profit}/{pair_loss} out of {pair_profit + pair_loss}")

total_profit += wallet - 100
print(f"Profit/Loss Ratio: {profit}/{loss} out of {profit + loss}\n"
      f"Win_Ratio = {profit / (profit + loss) * 100}, Loss_Ratio = {loss / (profit + loss) * 100}\n"
      f"Total Cash = ${wallet}, Growth Amount = ${total_profit}")
