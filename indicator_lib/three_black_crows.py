import talib


def calc_three_black_crows(dataframe):
    """calculate the three black crows indicator"""
    column_title = "ta_three_b_crows"
    # Calculate
    dataframe[column_title] = talib.CDL3BLACKCROWS(
        dataframe['open'],
        dataframe['high'],
        dataframe['low'],
        dataframe['close']
    )

    return dataframe
