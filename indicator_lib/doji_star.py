import talib

def doji_star(dataframe):
    """
    Function to calculate the doji star indicator. This is a candlestick pattern, more details can be found here:
    :param data: dataframe object where the Doji Star patterns should be detected on
    :return: dataframe with Doji Star patterns identified
    """
    # Copy the dataframe
    dataframe = dataframe.copy()
    # Add doji star column to dataframe
    dataframe['doji_star'] = 0
    # Calculate doji star on dataframe

    dataframe['doji_star'] = talib.CDLDOJISTAR(
        dataframe['open'],
        dataframe['high'],
        dataframe['low'],
        dataframe['close']
    )

    return dataframe
