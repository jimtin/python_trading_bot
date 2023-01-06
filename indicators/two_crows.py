import talib

# Function to calculate the two crows indicator
def calc_two_crows(dataframe):
    # Define new title for column
    column_title = "ta_two_crows"
    # Calculate
    dataframe[column_title] = talib.CDL2CROWS(
        dataframe['open'],
        dataframe['high'],
        dataframe['low'],
        dataframe['close']
    )
    return dataframe