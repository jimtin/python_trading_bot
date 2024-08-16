import talib


def calc_bollinger_bands(dataframe, timeperiod, std_dev_up, std_dev_down, mattype):
    """calculate Bollinger Bands"""
    upper_title = f"ta_bollinger_upper_{timeperiod}"
    lower_title = f"ta_bollinger_lower_{timeperiod}"
    middle_title = f"ta_bollinger_middle_{timeperiod}"

    dataframe[upper_title], dataframe[middle_title], dataframe[lower_title] = talib.BBANDS(
        close=dataframe['close'],
        timeperiod=timeperiod,
        nbdevup=std_dev_up,
        nbdevdn=std_dev_down,
        mattype=mattype
    )

    return dataframe
