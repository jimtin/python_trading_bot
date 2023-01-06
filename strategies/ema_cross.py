'''
Assumptions:
1. All strategy is performed on an existing dataframe. Previous inputs define how dataframe is retrieved/created
'''
from indicators import ema_cross
import display_lib


# Main display function
def ema_cross_strategy(dataframe, backtest=True, display=True, upload=False, project_settings=[]):
    # Determine EMA Cross Events for EMA 15 and EMA 200
    print("Calculating cross events for EMA 15 and EMA 200")
    ema_one = "ta_ema_15"
    ema_two = "ta_ema_200"
    cross_event_dataframe = ema_cross.ema_cross(
        dataframe=dataframe,
        ema_one=ema_one,
        ema_two=ema_two
    )
    order_dataframe = determine_order(
        dataframe=cross_event_dataframe,
        ema_one=ema_one,
        ema_two=ema_two,
        pip_size=0.01,
        risk_ratio=1
    )
    # Extract cross events
    cross_events = order_dataframe[order_dataframe['crossover'] == True]
    # Extract valid trades from cross_events
    valid_trades = cross_events[cross_events['valid'] == True]
    # Extract invalid trades from cross events
    invalid_trades = cross_events[cross_events['valid'] == False]
    if backtest:
        # Extract trade rows
        trade_dataframe = valid_trades[['time', 'human_time', 'order_type', 'stop_loss', 'stop_price', 'take_profit']]
    else:
        last_event = order_dataframe.tail(1)
        if last_event['valid'] == True:
            return last_event
        return False

    # Graph if display is true
    if display:
        # Update plotting
        fig = display_lib.construct_base_candlestick_graph(dataframe=cross_event_dataframe, candlestick_title="BTCUSD Raw")
        # Add ta_ema_15
        fig = display_lib.add_line_to_graph(
            base_fig=fig,
            dataframe=cross_event_dataframe,
            dataframe_column="ta_ema_15",
            line_name="EMA 15"
        )
        # Add ta_ema_200
        fig = display_lib.add_line_to_graph(
            base_fig=fig,
            dataframe=cross_event_dataframe,
            dataframe_column="ta_ema_200",
            line_name="EMA 15"
        )
        # Add cross event display
        fig = display_lib.add_markers_to_graph(
            base_fig=fig,
            dataframe=valid_trades,
            value_column="close",
            point_names="Valid Trades Cross Events"
        )
        # Add invalid trades
        fig = display_lib.add_markers_to_graph(
            base_fig=fig,
            dataframe=invalid_trades,
            value_column="close",
            point_names="Invalid Trades Cross Events"
        )
        if upload:
            display_lib.display_graph(fig, "BTCUSD Raw")
        # Display
        display_lib.display_graph(fig, "BTCUSD Raw Graph")
    return trade_dataframe


# Determine order type and values
def determine_order(dataframe, ema_one, ema_two, pip_size, risk_ratio, backtest=True):
    """

    :param dataframe:
    :param risk_amount:
    :param backtest:
    :return:
    """
    # Set up Pip movement
    # Determine direction
    dataframe['direction'] = dataframe[ema_one] > dataframe[ema_one].shift(1) # I.e. trending up
    # Add in stop loss
    dataframe['stop_loss'] = dataframe[ema_two]
    cross_events = dataframe
    # Calculate stop loss
    for index, row in cross_events.iterrows():
        if row['direction'] == True:
            # Order type will be a BUY_STOP
            cross_events.loc[index, 'order_type'] = "BUY_STOP"
            # Calculate the distance between the low and the stop loss
            if row['low'] > row['stop_loss']:
                take_profit = row['low'] - row['stop_loss']
            else:
                take_profit = row['stop_loss'] - row['low']
            # Multiply the take_profit by the risk amount
            take_profit = take_profit * risk_ratio
            # Set the take profit based upon the distance
            cross_events.loc[index, 'take_profit'] = row['high'] + take_profit
            # Set the entry price as 10 pips above the high
            stop_price = row['high'] + 10 * pip_size
            cross_events.loc[index, 'stop_price'] = stop_price

        else:
            # Order type will be a SELL STOP
            cross_events.loc[index, 'order_type'] = "SELL_STOP"
            if row['high'] > row['stop_loss']:
                take_profit = row['high'] - row['stop_loss']
            else:
                take_profit = row['stop_loss'] - row['high']
            # Multiply the take_profit by the risk amount
            take_profit = take_profit * risk_ratio
            # Set the take profit
            cross_events.loc[index, 'take_profit'] = row['low'] - take_profit
            # Set the entry price as 10 pips below the low
            stop_price = row['low'] - 10 * pip_size
            cross_events.loc[index, 'stop_price'] = stop_price

    for index, row in cross_events.iterrows():
        if row['crossover'] == True:
            if row['order_type'] == "BUY_STOP":
                valid = row['take_profit'] > row['stop_price']
                cross_events.loc[index, 'valid'] = valid
            elif row['order_type'] == "SELL_STOP":
                valid = row['stop_price'] > row['take_profit']
                cross_events.loc[index, 'valid'] = valid
            else:
                cross_events.loc[index, 'valid'] = False

    return cross_events

