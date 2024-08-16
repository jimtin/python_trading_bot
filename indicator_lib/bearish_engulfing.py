from indicator_lib import ema_calculator
from strategies import engulfing_candle_strategy


def calc_bearish_engulfing(dataframe, exchange, project_settings):
    """
    Function to detect a bearish engulfing pattern
    :param dataframe: Pandas dataframe of candle data
    :param exchange: string
    :param project_settings: JSON data object
    :return: Bool
    """

    # Extract the most & second most recent candle
    most_recent_candle = dataframe.loc[len(dataframe) - 1]  # .loc[-1]?
    second_most_recent_candle = dataframe.loc[len(dataframe) - 2]

    # Calculate if the second most recent candle is Green
    if second_most_recent_candle['close'] > second_most_recent_candle['open']:
        # Calculate if most recent candle is Red
        if most_recent_candle['close'] < most_recent_candle['open']:
            red_body = most_recent_candle['open'] - most_recent_candle['close']
            green_body = second_most_recent_candle['close'] - second_most_recent_candle['open']
            if red_body > green_body:
                # Compare Red low and Green low
                if most_recent_candle['low'] < second_most_recent_candle['low']:
                    ema_20 = ema_calculator.calc_ema(dataframe=dataframe, ema_size=20)
                    # Extract the second most recent candle from the new dataframe
                    ema_second_most_recent = ema_20.loc[len(ema_20) - 2]
                    if ema_second_most_recent['open'] > ema_second_most_recent['ema_20']:
                        # Use this function if you're planning on sending it to an alert generator
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
