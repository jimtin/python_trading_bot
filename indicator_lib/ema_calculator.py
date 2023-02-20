import pandas


# Define function to calculate an arbitrary EMA
def calc_ema(dataframe, ema_size):
    # Create column string
    ema_name = "ema_" + str(ema_size)
    # Create the multiplier
    multiplier = 2/(ema_size + 1)
    # Calculate the initial value (SMA)
    initial_mean = dataframe['close'].head(ema_size).mean()

    # Iterate through Dataframe
    for i in range(len(dataframe)):
        # If i equals the ema_size, substitute the first value (SMA)
        if i == ema_size:
            dataframe.loc[i, ema_name] = initial_mean
        # For subsequent values, use the previous EMA value to calculate the current row EMA
        elif i > ema_size:
            ema_value = dataframe.loc[i, 'close'] * multiplier + dataframe.loc[i-1, ema_name]*(1-multiplier)
            dataframe.loc[i, ema_name] = ema_value
        # Input a value of zero
        else:
            dataframe.loc[i, ema_name] = 0.00
    # Once loop completed, return the updated dataframe
    return dataframe