from indicator_lib import doji_star, rsi, ta_sma, ta_ema, two_crows, three_black_crows, bollinger_bands


def all_indicators(dataframe):
    """Calculate all the indicator_lib currently available"""
    df = dataframe.copy()

    for val in [5, 8, 15, 20, 50, 200]:  # SMA
        df = ta_sma.calc_ta_sma(df, val)

    for val in [5, 8, 15, 20, 50, 200]:  # EMA
        df = ta_ema.calc_ema(df, val)

    # Patterns
    df = two_crows.calc_two_crows(df)  # 2 Crows
    df = three_black_crows.calc_three_black_crows(df)  # Three black crows
    df = doji_star.doji_star(df)  # Doji Star
    df = rsi.rsi(df)  # RSI

    # Overlap Studies
    # df = bollinger_bands.calc_bollinger_bands(df, 20, 2, 2, 0)
    return df
