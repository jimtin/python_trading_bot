import talib

# Function to calculate Bollinger Bands
def calc_bollinger_bands(dataframe, timeperiod, std_dev_up, std_dev_down, mattype):
    # Create column titles
    upper_title = "ta_bollinger_upper_" + str(timeperiod)
    lower_title = "ta_bollinger_lower_" + str(timeperiod)
    middle_title = "ta_bollinger_middle_" + str(timeperiod)

    # Calculate
    dataframe[upper_title], dataframe[middle_title], dataframe[lower_title] = talib.BBANDS(
        close=dataframe['close'],
        timeperiod=timeperiod,
        nbdevup=std_dev_up,
        nbdevdn=std_dev_down,
        mattype=mattype
    )
    # Return the dataframe
    return dataframe