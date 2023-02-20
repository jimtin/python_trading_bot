import talib


# Function to calculate an EMA
def calc_ema(dataframe, periods):
    # Create the column title
    column_title = "ta_ema_" + str(periods)
    # Calculate
    dataframe[column_title] = talib.EMA(dataframe['close'], periods)
    # Return
    return dataframe
