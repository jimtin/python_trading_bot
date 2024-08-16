import MetaTrader5
import pandas
import datetime
import pytz

import exceptions


def start_mt5(username, password, server, path):
    """
    Initializes and logs into MT5
    :param username: 8 digit integer
    :param password: string
    :param server: string
    :param path: string
    :return: True if successful, Error if not
    """
    # Ensure that all variables are the correct type
    uname = int(username)
    pword = str(password)
    trading_server = str(server)
    filepath = str(path)

    # start MT5
    try:
        metaTrader_init = MetaTrader5.initialize(login=uname, password=pword, server=trading_server, path=filepath)
    except Exception as e:
        print(f"Error initializing MetaTrader: {e}")
        raise exceptions.MetaTraderInitializeError

    # login to MT5
    if not metaTrader_init:
        raise exceptions.MetaTraderInitializeError

    try:
        metaTrader_login = MetaTrader5.login(login=uname, password=pword, server=trading_server)
    except Exception as e:
        print(f"Error loging in to MetaTrader: {e}")
        raise exceptions.MetaTraderLoginError

    # Return True if initialization and login are successful
    if metaTrader_login:
        return True


def initialize_symbols(symbol_array):
    """
    Function to initialize a symbol on MT5. Note that different brokers have different symbols.
    To read more: https://trading-data-analysis.pro/everything-you-need-to-connect-your-python-trading-bot-to-metatrader-5-de0d8fb80053
    :param symbol_array: List of symbols to be initialized
    :return: True if all symbols enabled
    """
    # Get a list of all symbols supported in MT5
    all_symbols = MetaTrader5.symbols_get()
    symbol_names = []
    for symbol in all_symbols:
        symbol_names.append(symbol.name)

    # Check each provided symbol in symbol_array to ensure it exists
    for provided_symbol in symbol_array:
        if provided_symbol in symbol_names:
            # If it exists, enable
            if not MetaTrader5.symbol_select(provided_symbol, True):
                print(f"Error creating symbol {provided_symbol}. Symbol not enabled.")
                raise exceptions.MetaTraderSymbolUnableToBeEnabledError
        else:
            print(f"Symbol {provided_symbol} does not exist in this MT5 implementation. Symbol not enabled.")
            raise exceptions.MetaTraderSymbolDoesNotExistError

    return True  # all symbols enabled


# Function to place a trade on MT5
def place_order(order_type, symbol, volume, stop_loss, take_profit, comment, direct=False, price=0):
    """
    Function to place a trade on MetaTrader 5 with option to check balance first
    :param order_type: String from options: SELL_STOP, BUY_STOP, SELL, BUY
    :param symbol: String
    :param volume: String or Float
    :param stop_loss: String or Float
    :param take_profit: String of Float
    :param comment: String
    :param direct: Bool, defaults to False
    :param price: String or Float, optional
    :return: Trade outcome or syntax error
    """

    # Set up the place order request
    request = {
        "symbol": symbol,
        "volume": volume,
        "sl": round(stop_loss, 3),
        "tp": round(take_profit, 3),
        "type_time": MetaTrader5.ORDER_TIME_GTC,
        "comment": comment
    }

    # Create the order type based upon provided values. This can be expanded for different order types as needed.
    if order_type == "SELL_STOP":
        request['type'] = MetaTrader5.ORDER_TYPE_SELL_STOP
        request['action'] = MetaTrader5.TRADE_ACTION_PENDING
        if price <= 0:
            raise exceptions.MetaTraderIncorrectStopPriceError
        else:
            request['price'] = round(price, 3)
            request['type_filling'] = MetaTrader5.ORDER_FILLING_RETURN
    elif order_type == "BUY_STOP":
        request['type'] = MetaTrader5.ORDER_TYPE_BUY_STOP
        request['action'] = MetaTrader5.TRADE_ACTION_PENDING
        if price <= 0:
            raise exceptions.MetaTraderIncorrectStopPriceError
        else:
            request['price'] = round(price, 3)
            request['type_filling'] = MetaTrader5.ORDER_FILLING_RETURN

    elif order_type == "SELL":
        request['type'] = MetaTrader5.ORDER_TYPE_SELL
        request['action'] = MetaTrader5.TRADE_ACTION_DEAL
        request['type_filling'] = MetaTrader5.ORDER_FILLING_IOC
    elif order_type == "BUY":
        request['type'] = MetaTrader5.ORDER_TYPE_BUY
        request['action'] = MetaTrader5.TRADE_ACTION_DEAL
        request['type_filling'] = MetaTrader5.ORDER_FILLING_IOC
    else:
        print("Choose a valid order type from SELL_STOP, BUY_STOP, SELL, BUY")
        raise SyntaxError

    if direct is True:
        # Send the order to MT5
        order_result = MetaTrader5.order_send(request)
        # Notify based on return outcomes
        if order_result[0] == 10009:
            # Print result
            # print(f"Order for {symbol} successful") # Enable if error checking order_result
            return order_result[2]
        elif order_result[0] == 10027:
            # Turn off autotrading
            print(f"Turn off Algo Trading on MT5 Terminal")
            raise exceptions.MetaTraderAlgoTradingNotDisabledError
        else:
            # Print result
            print(f"Error placing order. ErrorCode {order_result[0]}, Error Details: {order_result}")
            raise exceptions.MetaTraderOrderPlacingError

    else:
        # Check the order
        result = MetaTrader5.order_check(request)
        if result[0] != 0:
            print(f"Order unsucessful. Details: {result}")
            raise exceptions.MetaTraderOrderCheckError

        # print("Balance Check Successful") # Enable to error check Balance Check
        # If order check is successful, place the order. Little bit of recursion for fun.
        place_order(
            order_type=order_type,
            symbol=symbol,
            volume=volume,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            comment=comment,
            direct=True
        )


# Function to cancel an order
def cancel_order(order_number):
    """
    Function to cancel an order
    :param order_number: Int
    :return:
    """
    # Create the request
    request = {
        "action": MetaTrader5.TRADE_ACTION_REMOVE,
        "order": order_number,
        "comment": "Order Removed"
    }
    # Send order to MT5
    order_result = MetaTrader5.order_send(request)
    if order_result[0] != 10009:
        print(f"Error cancelling order. Details: {order_result}")
        raise exceptions.MetaTraderCancelOrderError

    return True


def modify_position(order_number, symbol, new_stop_loss, new_take_profit):
    """
    Function to modify a position
    :param order_number: Int
    :param symbol: String
    :param new_stop_loss: Float
    :param new_take_profit: Float
    :return: Boolean
    """
    # Create the request
    request = {
        "action": MetaTrader5.TRADE_ACTION_SLTP,
        "symbol": symbol,
        "sl": new_stop_loss,
        "tp": new_take_profit,
        "position": order_number
    }
    # Send order to MT5
    order_result = MetaTrader5.order_send(request)
    if order_result[0] != 10009:
        print(f"Error modifying position. Details: {order_result}")
        raise exceptions.MetaTraderModifyPositionError

    return True


def get_open_orders():
    """
    Function to retrieve a list of open orders from MetaTrader 5
    :return: List of open orders
    """
    orders = MetaTrader5.orders_get()
    order_array = []
    for order in orders:
        order_array.append(order[0])
    return order_array


def get_open_positions():
    """
    Function to retrieve a list of open orders from MetaTrader 5
    :return: list of positions
    """
    positions = MetaTrader5.positions_get()
    return positions


def close_position(order_number, symbol, volume, order_type, price, comment):
    """
    Function to close an open position from MetaTrader 5
    :param order_number: int
    :return: Boolean
    """
    # Create the request
    request = {
        'action': MetaTrader5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': volume,
        'position': order_number,
        'price': price,
        'type_time': MetaTrader5.ORDER_TIME_GTC,
        'type_filling': MetaTrader5.ORDER_FILLING_IOC,
        'comment': comment
    }

    if order_type == "SELL":
        request['type'] = MetaTrader5.ORDER_TYPE_SELL
    elif order_type == "BUY":
        request['type'] = MetaTrader5.ORDER_TYPE_BUY
    else:
        print(f"Incorrect syntax for position close {order_type}")
        raise SyntaxError

    # Place the order
    result = MetaTrader5.order_send(request)
    if result[0] != 10009:
        print(f"Error closing position. Details: {result}")
        raise exceptions.MetaTraderClosePositionError

    return True


# Function to convert a timeframe string in MetaTrader 5 friendly format
def set_query_timeframe(timeframe):
    switch = {
        "M1": MetaTrader5.TIMEFRAME_M1,
        "M2": MetaTrader5.TIMEFRAME_M2,
        "M3": MetaTrader5.TIMEFRAME_M3,
        "M4": MetaTrader5.TIMEFRAME_M4,
        "M5": MetaTrader5.TIMEFRAME_M5,
        "M6": MetaTrader5.TIMEFRAME_M6,
        "M10": MetaTrader5.TIMEFRAME_M10,
        "M12": MetaTrader5.TIMEFRAME_M12,
        "M15": MetaTrader5.TIMEFRAME_M15,
        "M20": MetaTrader5.TIMEFRAME_M20,
        "M30": MetaTrader5.TIMEFRAME_M30,

        "H1": MetaTrader5.TIMEFRAME_H1,
        "H2": MetaTrader5.TIMEFRAME_H2,
        "H3": MetaTrader5.TIMEFRAME_H3,
        "H4": MetaTrader5.TIMEFRAME_H4,
        "H6": MetaTrader5.TIMEFRAME_H6,
        "H8": MetaTrader5.TIMEFRAME_H8,
        "H12": MetaTrader5.TIMEFRAME_H12,

        "D1": MetaTrader5.TIMEFRAME_D1,
        "W1": MetaTrader5.TIMEFRAME_W1,
        "MN1": MetaTrader5.TIMEFRAME_MN1,
    }

    if timeframe not in switch:
        print(f"Incorrect timeframe provided. {timeframe}")
        raise ValueError

    return switch[timeframe]


def query_historic_data(symbol, timeframe, number_of_candles):
    """query previous candlestick data from MT5"""
    # Convert the timeframe into an MT5 friendly format
    mt5_timeframe = set_query_timeframe(timeframe)
    # Retrieve data from MT5
    rates = MetaTrader5.copy_rates_from_pos(symbol, mt5_timeframe, 1, number_of_candles)
    return rates


def retrieve_latest_tick(symbol):
    """
    Function to retrieve the latest tick for a symbol
    :param symbol: String
    :return: Dictionary object
    """
    # Retrieve the tick information
    tick = MetaTrader5.symbol_info_tick(symbol)._asdict()
    tick['spread'] = tick['ask'] - tick['bid']
    return tick


def retrieve_tick_time_range(start_time_utc, finish_time_utc, symbol, dataframe=False):
    """retrieve ticks from a time range"""
    # Set option in MT5 terminal for Unlimited bars
    # Check time format of start time
    if type(start_time_utc) != datetime.datetime:
        print(f"Time range tick start time is in incorrect format")
        raise ValueError
    # Check time format of finish time
    if type(finish_time_utc) != datetime.datetime:
        print(f"Time range tick finish time is in incorrect format")
        raise ValueError
    # Retrieve ticks
    ticks = MetaTrader5.copy_ticks_range(symbol, start_time_utc, finish_time_utc, MetaTrader5.COPY_TICKS_INFO)
    # Convert into dataframe only if Dataframe set to True
    if dataframe:
        ticks_data_frame = pandas.DataFrame(ticks)
        ticks_data_frame['spread'] = ticks_data_frame['ask'] - ticks_data_frame['bid']
        ticks_data_frame['symbol'] = symbol
        # Format integers into signed integers (postgres doesn't support unsigned int)
        ticks_data_frame['time'] = ticks_data_frame['time'].astype('int64')
        ticks_data_frame['volume'] = ticks_data_frame['volume'].astype('int64')
        ticks_data_frame['time_msc'] = ticks_data_frame['time_msc'].astype('int64')
        return ticks_data_frame
    return ticks


def retrieve_candlestick_data_range(start_time_utc, finish_time_utc, symbol, timeframe, dataframe=False):
    """retrieve candlestick data for a specified time range"""
    # Set option in MT5 terminal for Unlimited bars
    # Check time format of start time
    if type(start_time_utc) != datetime.datetime:
        print(f"Time range tick start time is in incorrect format")
        raise ValueError
    # Check time format of finish time
    if type(finish_time_utc) != datetime.datetime:
        print(f"Time range tick finish time is in incorrect format")
        raise ValueError
    # Convert the timeframe into MT5 compatible format
    timeframe_value = set_query_timeframe(timeframe)
    # Retrieve the data
    candlestick_data = MetaTrader5.copy_rates_range(symbol, timeframe_value, start_time_utc, finish_time_utc)
    if dataframe:
        candlestick_dataframe = pandas.DataFrame(candlestick_data)
        candlestick_dataframe['symbol'] = symbol
        candlestick_dataframe['timeframe'] = timeframe
        # Convert integers into signed integers (postgres doesn't support unsigned int)
        candlestick_dataframe['time'] = candlestick_dataframe['time'].astype('int64')
        candlestick_dataframe['tick_volume'] = candlestick_dataframe['tick_volume'].astype('float64')
        candlestick_dataframe['spread'] = candlestick_dataframe['spread'].astype('int64')
        candlestick_dataframe['real_volume'] = candlestick_dataframe['real_volume'].astype('int64')
        return candlestick_dataframe
    return candlestick_data
