import talib

# Function to calculate an SMA with TA-Lib
def calc_ta_sma(dataframe, periods):
    # Define new title for column
    column_title = "ta_sma_" + str(periods)
    # Calculate
    dataframe[column_title] = talib.SMA(dataframe['close'], periods)
    # Return dataframe
    return dataframe