import time

from binance.spot import Spot
import datetime
import pandas as pd
import yfinance as yf

PAIRS = ["SOL-USD"]


def get_yahoo(pair):
    symbol = str(pair)  # Symbol of the desired stock

    # define start & dates
    start = (datetime.date.today() - datetime.timedelta(6))
    end = datetime.date.today()
    # pull data
    dataframe = yf.download(symbol, start=start, end=end, interval="1m")
    dataframe.to_csv("yahoo_data.csv")


# startTime=klines[0][0]-LIMIT*MILLISECONDS
def get_binance_data(currency_pair):
    client = Spot()
    candles = client.klines(currency_pair, "1m", limit=1000)
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

    for _ in range(5):
        data_container = []
        candles = client.klines(currency_pair, "1m", limit=1000, endTime=candles[0][6] - 60000)
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


# get_yahoo("SOL-USD")
df = get_binance_data("SOLUSDT")
df.to_csv("test_cust.csv")
