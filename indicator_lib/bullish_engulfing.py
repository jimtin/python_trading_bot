from indicator_lib import ema_calculator
from strategies import engulfing_candle_strategy


def calc_bullish_engulfing(dataframe, exchange, project_settings):
    """
    Function to calculate if a bullish engulfing candle has been detected
    :param dataframe: Pandas dataframe of candle data
    :param exchange: string
    :param project_settings: JSON data object
    :return: Bool
    """
    # Extract the most & the second most recent candles
    most_recent_candle = dataframe.loc[len(dataframe) - 1]
    second_most_recent_candle = dataframe.loc[len(dataframe) - 2]

    # Calculate if second most recent candle Red
    if second_most_recent_candle['close'] < second_most_recent_candle['open']:
        # Calculate if most recent candle green
        if most_recent_candle['close'] > most_recent_candle['open']:
            # Check the Green Body > Red Body
            red_body = second_most_recent_candle['open'] - second_most_recent_candle['close']
            green_body = most_recent_candle['close'] - second_most_recent_candle['open']
            if green_body > red_body:
                # Compare Green High > Red High
                if most_recent_candle['high'] > second_most_recent_candle['high']:
                    # Calculate the 20-EMA
                    ema_20 = ema_calculator.calc_ema(dataframe=dataframe, ema_size=20)
                    ema_second_most_recent = ema_20.loc[len(ema_20) - 2]  # the second most recent candle
                    if ema_second_most_recent['close'] < ema_second_most_recent['ema_20']:
                        # If plugging into a strategy such as the Engulfing Candle Strategy, send to alerting mechanism
                        strategy = engulfing_candle_strategy.engulfing_candle_strategy(
                            high=most_recent_candle['high'],
                            low=most_recent_candle['low'],
                            symbol=most_recent_candle['symbol'],
                            timeframe=most_recent_candle['timeframe'],
                            exchange=exchange,
                            alert_type="bullish_engulfing",
                            project_settings=project_settings
                        )
                        return True
    return False
