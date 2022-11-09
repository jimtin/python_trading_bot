


# Function to respond to engulfing candle detections and turn them into a strategy
def engulfing_candle_strategy(high, low, symbol, timeframe, exchange, alert_type, project_settings):
    """
    Function to respond to engulfing candle detections and turn them into a strategy
    :param high: float
    :param low: float
    :param symbol: string
    :param timeframe: string
    :param exchange: string
    :param alert_type: string
    :param project_settings: json dictionary object
    :return:
    """
    # Only apply strategy to specified timeframes
    if timeframe == "M15" or timeframe == "M30" or timeframe == "H1" or timeframe == "D1":
        # Respond to bullish_engulfing
        if alert_type == "bullish_engulfing":
            # Set the Trade Type
            trade_type = "BUY"
            # Set the Take Profit
            take_profit = high + high - low
            # Set the Buy Stop
            entry_price = high
            # Set the Stop Loss
            stop_loss = low
        elif alert_type == "bearish_engulfing":
            # Set the Trade Type
            trade_type = "SELL"
            # Set the Take Profit
            take_profit = low - high + low
            # Set the Sell Stop
            entry_price = low
            # Set the Stop Loss
            stop_loss = high
        # Print the result to the screen
        print(f"Trade Signal Detected. Symbol: {symbol}, Trade Type: {trade_type}, Take Profit: {take_profit}, "
              f"Entry Price: {entry_price}, Stop Loss: {stop_loss}, Exchange: {exchange}")
