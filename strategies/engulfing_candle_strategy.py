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
    if timeframe in ["M15", "M30", "H1", "D1"]:
        if alert_type == "bullish_engulfing":
            trade_type = "BUY"
            take_profit = high + high - low
            entry_price = high
            stop_loss = low
        elif alert_type == "bearish_engulfing":
            trade_type = "SELL"
            take_profit = low - high + low
            entry_price = low
            stop_loss = high
        else:
            raise Exception

        print(f"Trade Signal Detected. Symbol: {symbol}, Trade Type: {trade_type}, Take Profit: {take_profit}, "
              f"Entry Price: {entry_price}, Stop Loss: {stop_loss}, Exchange: {exchange}")
