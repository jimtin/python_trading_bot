import requests
import pandas

# Function to get candle data
def get_candlestick_data(symbol, timeframe):
    # Convert the timeframe into a Coinbase specific type. This could be done in a switch statement for Python 3.10
    if timeframe == "M1":
        timeframe_converted = 60
    elif timeframe == "M5":
        timeframe_converted = 300
    elif timeframe == "M15":
        timeframe_converted = 900
    elif timeframe == "H1":
        timeframe_converted = 3600
    elif timeframe == "H6":
        timeframe_converted = 21600
    elif timeframe == "D1":
        timeframe_converted = 86400
    else:
        return Exception
    # Construct the URL
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={timeframe_converted}"
    # Construct the headers
    headers = {"accept": "application/json"}
    # Query the API
    response = requests.get(url, headers=headers)
    # Retrieve the data
    candlestick_raw_data = response.json()
    # Initialize an empty array
    candlestick_data = []
    # Iterate through the returned data and construct a more useful data format
    for candle in candlestick_raw_data:
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
        # Append to candlestick_data
        candlestick_data.append(candle_dict)
    # Convert candlestick_data to dataframe
    candlestick_dataframe = pandas.DataFrame(candlestick_data)
    # Return a dataframe
    return candlestick_dataframe
