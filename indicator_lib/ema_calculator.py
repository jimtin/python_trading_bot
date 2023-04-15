import pandas


def calc_ema(dataframe, ema_size):
    ema_name = f"ema_{ema_size}"  # column string
    multiplier = 2/(ema_size + 1)
    # Calculate the initial value (SMA)
    initial_mean = dataframe['close'].head(ema_size).mean()

    for i in range(len(dataframe)):
        if i == ema_size:  # substitute the first value (SMA)
            dataframe.loc[i, ema_name] = initial_mean
        # For subsequent values, use the previous EMA value to calculate the current row EMA
        elif i > ema_size:
            ema_value = dataframe.loc[i, 'close'] * multiplier + dataframe.loc[i-1, ema_name]*(1-multiplier)
            dataframe.loc[i, ema_name] = ema_value
        else:
            dataframe.loc[i, ema_name] = 0.0

    return dataframe
