import pandas
import time
from sql_lib import sql_interaction


# Function to backtest a strategy
def backtest(valid_trades_dataframe, time_valid, tick_data_table, project_settings):
    print("Starting Backtest script")
    # Make sure that SettingWithCopyWarning suppressed
    pandas.options.mode.chained_assignment = None
    # todo: Save the valid trades into a postgres table
    # todo: Sort valid_trades_dataframe by time
    # Add status of pending to orders
    valid_trades_dataframe['status'] = "pending"
    valid_trades_dataframe['time_valid'] = valid_trades_dataframe['time'] + time_valid
    # Retrieve the tick data
    tick_dataframe_generator_object = sql_interaction.retrieve_dataframe(tick_data_table, project_settings, chunky=True,
                                                                         tick_data=True)
    # Set up trade array
    trade_list = []
    # Setup open_orders
    open_orders = pandas.DataFrame()
    # Setup open positions
    open_buy_positions = pandas.DataFrame()
    open_sell_positions = pandas.DataFrame()
    # Setup closed
    print("Data retrieved, analysis starting")
    for chunk in tick_dataframe_generator_object:
        tic = time.perf_counter()
        #print("New Chunk Being Analyzed")
        # Format time_msc into the milliseconds it should be
        chunk['time_msc'] = chunk['time_msc'] / 1000
        # Convert into a dictionary
        # df_dict = chunk.to_dict('records')
        for index, row in chunk.iterrows():
            # Step 1: Check for orders which have become valid
            mask = (valid_trades_dataframe['time'] < row['time_msc'])
            if len(valid_trades_dataframe[mask]) > 0:
                print(f"TickTime: {row['time_msc']}. Order became valid")
                # Retrieve the valid order
                new_data_frame = valid_trades_dataframe[mask]
                # Update status
                open_orders = new_order(order_dataframe=open_orders, new_order=new_data_frame)
                # Drop from valid trades dataframe
                valid_trades_dataframe = valid_trades_dataframe.drop(valid_trades_dataframe[mask].index)
            # Step 2: Check open orders for those which are no longer valid or have reached STOP PRICE
            if len(open_orders) > 0:
                # Check open orders for those which have expired
                mask = (open_orders['time_valid'] < row['time_msc'])
                if len(open_orders[mask]) > 0:
                    #print(f"TickTime: {row['time_msc']}. Order no longer valid. Order: {open_orders[mask]}")
                    open_orders = expire_order(open_orders, open_orders[mask])
                # Check if BUY_STOP reached
                mask = (open_orders['order_type'] == "BUY_STOP") & (open_orders['stop_price'] >= row['bid'])
                if len(open_orders[mask]) > 0:
                    #print(f"BUY_STOP price Reached. Time: {row['time_msc']}, Row Bid Price: {row['bid']}, BUY_ORDERS: {open_orders[mask]['stop_price']}")
                    # Add to Open Buy Positions
                    open_buy_positions = new_position(open_buy_positions, open_orders[mask])
                    # Drop from open orders as now a position
                    open_orders = open_orders.drop(open_orders[mask].index)
                # Check if SELL_STOP reached
                mask = (open_orders['order_type'] == "SELL_STOP") & (open_orders['stop_price'] <= row['bid'])
                if len(open_orders[mask]) > 0:
                    # Add to open_sell_positions
                    open_sell_positions = new_position(open_sell_positions, open_orders[mask])
                    open_orders = open_orders.drop(open_orders[mask].index)
            # Step 3: Check open positions to check their progress
            # Check open buy positions
            if len(open_buy_positions) > 0:
                # Check if any open buy positions have reached their TAKE_PROFIT
                mask = (open_buy_positions['take_profit'] <= row['bid'])
                if len(open_buy_positions[mask]) > 0:
                    # Todo: Add function with SQL to track
                    open_buy_positions = buy_take_profit_reached(
                        position_dataframe = open_buy_positions,
                        position=open_buy_positions[mask],
                        row=row
                    )
                # Check if any open buy positions have reached their STOP_LOSS
                mask = (open_buy_positions['stop_loss'] >= row['bid'])
                if len(open_buy_positions[mask]) > 0:
                    # Todo: Add function with SQL to track
                    open_buy_positions = buy_take_profit_reached(
                        position_dataframe=open_buy_positions,
                        position=open_buy_positions[mask],
                        row=row
                    )
            # Check open sell positions
            if len(open_sell_positions) > 0:
                # Check if any open sell positions have reached their TAKE_PROFIT
                mask = (open_sell_positions['take_profit'] >= row['bid'])
                if len(open_sell_positions[mask]) > 0:
                    # Todo: Add function with SQL to track
                    open_sell_positions = sell_take_profit_reached(
                        position_dataframe=open_buy_positions,
                        position=open_buy_positions[mask],
                        row=row
                    )
                # Check if any open sell positions have reached a stop loss
                mask = (open_sell_positions['stop_loss'] <= row['bid'])
                if len(open_sell_positions[mask]) > 0:
                    open_sell_positions = sell_take_profit_reached(
                        position_dataframe=open_buy_positions,
                        position=open_buy_positions[mask],
                        row=row
                    )


        toc = time.perf_counter()
        print(f"Time taken: {toc - tic:0.4f} seconds")


# Function to add a new order
def new_order(order_dataframe, new_order, project_settings=[]):
    # todo: Update SQL Table with outcomes
    # Update status of new_order dataframe
    new_order['status'] = "order"
    # Append to order_dataframe
    order_dataframe = pandas.concat([order_dataframe, new_order])
    return order_dataframe


# Function to expire an order
def expire_order(order_dataframe, expired_order, project_settings=[]):
    # todo: Update SQL Table with outcomes
    # Update status of expired_order
    expired_order['status'] = "expired"
    # Drop from order_dataframe
    updated_order_dataframe = order_dataframe.drop(expired_order.index)
    print(f"Order expired {expired_order}")
    # Return updated order dataframe
    return updated_order_dataframe


# Function to add a new position
def new_position(position_dataframe, new_position, project_settings=[]):
    # todo: Update SQL Table with outcome
    # Update status of order
    new_position['status'] = "position"
    print(f"Appending {new_position} to position_dataframe")
    # Append to position dataframe
    position_dataframe = pandas.concat([position_dataframe, new_position])
    return position_dataframe


# Function when a BUY Take Profit Reached
def buy_take_profit_reached(position_dataframe, position, row, project_settings=[]):
    # todo: Update SQL Table with outcome
    # Update status of position
    position['status'] = "closed"
    print(f"BUY Take Profit Reached. Price: {row['bid']}. ID: {position.index}")
    # Remove from position dataframe
    position_dataframe = position_dataframe.drop(position.index)
    return position_dataframe


# Function when a BUY Stop Loss reached
def buy_stop_loss_reached(position_dataframe, position, row, project_settings=[]):
    # todo: Update SQL Table with outcome
    # Update status of position
    position['status'] = "closed"
    print(f"BUY Stop Loss Reached. Price: {row['bid']}. ID: {position.index}")
    position_dataframe = position_dataframe.drop(position.index)
    return position_dataframe


# Function when a SELL Take Profit reached
def sell_take_profit_reached(position_dataframe, position, row, project_settings=[]):
    # todo: Update SQL Table with outcome
    # Update status of position
    position['status'] = 'closed'
    print(f"SELL Stop Loss Reached. Price: {row['bid']}. ID: {position.index}")
    position_dataframe = position_dataframe.drop(position.index)
    return position_dataframe


# Function when a SELL Stop Loss reached
def sell_stop_loss_reached(position_dataframe, position, row, project_settings=[]):
    # todo: Update SQL Table with outcome
    # Update status of position
    position['status'] = "closed"
    print(f"SELL Stop Loss Reached. Price: {row['bid']}. ID: {position.index}")
    position_dataframe = position_dataframe.drop(position.index)
    return position_dataframe

