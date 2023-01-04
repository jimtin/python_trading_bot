from indicators import ta_sma, ta_ema

# Calculate all the indicators currently available
def all_indicators(dataframe):
    # SMA's
    dataframe = ta_sma.calc_ta_sma(dataframe, 5)
    dataframe = ta_sma.calc_ta_sma(dataframe, 8)
    dataframe = ta_sma.calc_ta_sma(dataframe, 15)
    dataframe = ta_sma.calc_ta_sma(dataframe, 20)
    dataframe = ta_sma.calc_ta_sma(dataframe, 50)
    dataframe = ta_sma.calc_ta_sma(dataframe, 200)
    # EMA's
    dataframe = ta_ema.calc_ema(dataframe, 5)
    dataframe = ta_ema.calc_ema(dataframe, 8)
    dataframe = ta_ema.calc_ema(dataframe, 15)
    dataframe = ta_ema.calc_ema(dataframe, 20)
    dataframe = ta_ema.calc_ema(dataframe, 50)
    dataframe = ta_ema.calc_ema(dataframe, 200)
    return dataframe