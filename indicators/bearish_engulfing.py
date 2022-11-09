from indicators import ema_calculator
from strategies import engulfing_candle_strategy


# Function to calculate bearish engulfing pattern
def calc_bearish_engulfing(dataframe, exchange, project_settings):
    """
    Function to detect a bearish engulfing pattern
    :param dataframe: Pandas dataframe of candle data
    :param exchange: string
    :param project_settings: JSON data object
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
                        strategy = engulfing_candle_strategy.engulfing_candle_strategy(
                            high=most_recent_candle['high'],
                            low=most_recent_candle['low'],
                            symbol=most_recent_candle['symbol'],
                            timeframe=most_recent_candle['timeframe'],
                            exchange=exchange,
                            alert_type="bearish_engulfing",
                            project_settings=project_settings
                        )
                        return True
    return False