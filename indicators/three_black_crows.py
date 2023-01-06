import talib


# Function to calculate the three black crows indicator
def calc_three_black_crows(dataframe):
    # Define a new title for the column
    column_title = "ta_three_b_crows"
    # Calculate
    dataframe[column_title] = talib.CDL3BLACKCROWS(
        dataframe['open'],
        dataframe['high'],
        dataframe['low'],
        dataframe['close']
    )
    return dataframe