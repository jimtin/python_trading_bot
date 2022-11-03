from indicators import ema_calculator


# Function to calculate bullish engulfing pattern
def calc_bullish_engulfing(dataframe):
    """
    Function to calculate if a bullish engulfing candle has been detected
    :param dataframe: Pandas dataframe of candle data
    :return: Bool
    """
    # Extract the most recent candle
    len_most_recent = len(dataframe) - 1
    most_recent_candle = dataframe.loc[len_most_recent]

    # Extract the second most recent candle
    len_second_most_recent = len(dataframe) - 2
    second_most_recent_candle = dataframe.loc[len_second_most_recent]

    # Calculate if second most recent candle Red
    if second_most_recent_candle['close'] < second_most_recent_candle['open']:
        # Calculate if most recent candle green
        if most_recent_candle['close'] > most_recent_candle['open']:
            # Check the Green Body > Red Body
            # Red Body
            red_body = second_most_recent_candle['open'] - second_most_recent_candle['close']
            # Green Body
            green_body = most_recent_candle['close'] - second_most_recent_candle['open']
            # Compare
            if green_body > red_body:
                # Compare Green High > Red High
                if most_recent_candle['high'] > second_most_recent_candle['high']:
                    # Calculate the 20-EMA
                    ema_20 = ema_calculator.calc_ema(dataframe=dataframe, ema_size=20)
                    # Extract the second most recent candle from the new dataframe
                    ema_count = len(ema_20) - 2
                    ema_second_most_recent = ema_20.loc[ema_count]
                    print(ema_second_most_recent)
                    # Compare the EMA and Red Low
                    if ema_second_most_recent['close'] < ema_second_most_recent['ema_20']:
                        return True
    return False


