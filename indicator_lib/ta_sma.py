import talib


def calc_ta_sma(dataframe, periods):
    """calculate an SMA with TA-Lib"""
    df = dataframe.copy()
    column_title = f"ta_sma_{periods}"
    df[column_title] = talib.SMA(df['close'], periods)  # Calculate

    return df
