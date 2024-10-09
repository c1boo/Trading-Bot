# Import libraries
import json
import requests

# Defining Binance API URL
key = "https://api.binance.com/api/v3/ticker/price?symbol="

# Making list for multiple crypto's
currencies = ["BTCUSDT", "DOGEUSDT", "LTCUSDT"]
j = 0

# running loop to print all crypto prices
for i in currencies:
    # completing API for request
    url = key + currencies[j]
    data = requests.get(url)
    data = data.json()
    j = j + 1
    print(f"{data['symbol']} price is {data['price']}")


def get_data(pair):
    symbol = str(pair)  # Symbol of the desired stock

    # define start & dates
    start = (datetime.date.today() - datetime.timedelta(NUM_DAYS))
    end = datetime.date.today()
    # pull data
    dataframe = yf.download(symbol, start=start, end=end, interval=INTERVAL)
    return dataframe