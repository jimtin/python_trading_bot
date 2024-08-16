import talib


def calc_two_crows(dataframe):
    """calculate the two crows indicator"""
    column_title = "ta_two_crows"
    # Calculate
    dataframe[column_title] = talib.CDL2CROWS(
        dataframe['open'],
        dataframe['high'],
        dataframe['low'],
        dataframe['close']
    )
    return dataframe
