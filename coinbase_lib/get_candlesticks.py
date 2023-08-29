import requests
import pandas as pd


# Function to get candle data
def get_candlestick_data(symbol, timeframe):
    switch = {
        "M1": 60,
        "M5": 300,
        "M15": 900,
        "H1": 3600,
        "H6": 21600,
        "D1": 86400
    }

    if timeframe not in switch:
        raise Exception
    timeframe_converted = switch[timeframe]

    # Query the API
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={timeframe_converted}"
    headers = {"accept": "application/json"}
    candlestick_raw_data = requests.get(url, headers=headers).json()

    candlestick_data = []
    for candle in candlestick_raw_data:  # more useful data format
        candle_dict = {
            "symbol": symbol,
            "time": candle[0],
            "low": candle[1],
            "high": candle[2],
            "open": candle[3],
            "close": candle[4],
            "volume": candle[5],
            "timeframe": timeframe
        }
        candlestick_data.append(candle_dict)

    candlestick_dataframe = pd.DataFrame(candlestick_data)
    return candlestick_dataframe
