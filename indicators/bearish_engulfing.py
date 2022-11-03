from indicators import ema_calculator


# Function to calculate bearish engulfing pattern
def calc_bearish_engulfing(dataframe):
    """
    Function to detect a bearish engulfing pattern
    :param dataframe: Pandas dataframe of candle data
    :return: Bool
    """

    # Extract the most recent candle
    len_most_recent = len(dataframe) - 1
    most_recent_candle = dataframe.loc[len_most_recent]

    # Extract the second most recent candle
    len_second_most_recent = len(dataframe) - 2
    second_most_recent_candle = dataframe.loc[len_second_most_recent]

    # Calculate if the second most recent candle is Green
    if second_most_recent_candle['close'] > second_most_recent_candle['open']:
        # Calculate if most recent candle is Red
        if most_recent_candle['close'] < most_recent_candle['open']:
            # Check the Red Body > Red Body
            # Red Body
            red_body = most_recent_candle['open'] - most_recent_candle['close']
            # Green Body
            green_body = second_most_recent_candle['close'] - second_most_recent_candle['open']
            # Compare
            if red_body > green_body:
                # Compare Red low and Green low
                if most_recent_candle['low'] < second_most_recent_candle['low']:
                    # Calculate the 20-EMA
                    ema_20 = ema_calculator.calc_ema(dataframe=dataframe, ema_size=20)
                    # Extract the second most recent candle from the new dataframe
                    ema_count = len(ema_20) - 2
                    ema_second_most_recent = ema_20.loc[ema_count]
                    # Compare 20-EMA and Green Open
                    if ema_second_most_recent['open'] > ema_second_most_recent['ema_20']:
                        return True
    return False