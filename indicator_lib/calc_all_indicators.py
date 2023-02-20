from indicator_lib import doji_star, ta_sma, ta_ema, two_crows, three_black_crows, bollinger_bands

# Calculate all the indicator_lib currently available
def all_indicators(dataframe):
    # Copy the dataframe
    dataframe_copy = dataframe.copy()
    # SMA's
    dataframe_copy = ta_sma.calc_ta_sma(dataframe_copy, 5)
    dataframe_copy = ta_sma.calc_ta_sma(dataframe_copy, 8)
    dataframe_copy = ta_sma.calc_ta_sma(dataframe_copy, 15)
    dataframe_copy = ta_sma.calc_ta_sma(dataframe_copy, 20)
    dataframe_copy = ta_sma.calc_ta_sma(dataframe_copy, 50)
    dataframe_copy = ta_sma.calc_ta_sma(dataframe_copy, 200)
    # EMA's
    dataframe_copy = ta_ema.calc_ema(dataframe_copy, 5)
    dataframe_copy = ta_ema.calc_ema(dataframe_copy, 8)
    dataframe_copy = ta_ema.calc_ema(dataframe_copy, 15)
    dataframe_copy = ta_ema.calc_ema(dataframe_copy, 20)
    dataframe_copy = ta_ema.calc_ema(dataframe_copy, 50)
    dataframe_copy = ta_ema.calc_ema(dataframe_copy, 200)
    # Patterns
    # 2 Crows
    dataframe_copy = two_crows.calc_two_crows(dataframe_copy)
    dataframe_copy = three_black_crows.calc_three_black_crows(dataframe_copy)
    dataframe_copy = doji_star.doji_star(dataframe_copy)
    # Overlap Studies
    #dataframe = bollinger_bands.calc_bollinger_bands(dataframe, 20, 2, 2, 0)
    return dataframe_copy