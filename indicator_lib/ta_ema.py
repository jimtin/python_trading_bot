import talib


def calc_ema(dataframe, periods):
    """calculate EMA"""
    column_title = f"ta_ema_{periods}"
    dataframe[column_title] = talib.EMA(dataframe['close'], periods)  # Calculate
    return dataframe
