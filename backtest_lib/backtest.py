import pandas
import time
from sql_lib import sql_interaction


# Function to backtest a strategy
def backtest(valid_trades_dataframe, time_valid, tick_data_table, project_settings):
    print("Starting Backtest script")
    # todo: Save the valid trades into a postgres table
    # todo: Sort valid_trades_dataframe by time
    # Add status of pending to orders
    valid_trades_dataframe['status'] = "pending"
    valid_trades_dataframe['time_valid'] = valid_trades_dataframe['time'] + time_valid
    #print(valid_trades_dataframe)
    # Retrieve the tick data
    tick_dataframe_generator_object = sql_interaction.retrieve_dataframe(tick_data_table, project_settings, chunky=True,
                                                                         tick_data=True)
    # Set up trade array
    trade_list = []
    # Setup open_orders
    open_orders = pandas.DataFrame()
    # Setup open positions
    open_positions = pandas.DataFrame()
    # Setup closed
    print("Data retrieved, analysis starting")
    for chunk in tick_dataframe_generator_object:
        #tic = time.perf_counter()
        #print("New Chunk Being Analyzed")
        # Format time_msc into the milliseconds it should be
        chunk['time_msc'] = chunk['time_msc'] / 1000
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
                    print(f"TickTime: {row['time_msc']}. Order no longer valid. Order: {open_orders[mask]}")
                    # Todo: send to function which will also update the SQL Table
                    open_orders = open_orders.drop(open_orders[mask].index)
                # Check if BUY_STOP reached
                mask = (open_orders['order_type'] == "BUY_STOP" and open_orders['stop_price'] >= row['bid'])
                if len(open_orders[mask]) > 0:
                    print("BUY_STOP price Reached")
                # Check if SELL_STOP reached
                mask = (open_orders['order_type'] == "SELL_STOP" and open_orders['stop_price'] <= row['bid'])
                if len(open_orders[mask]) > 0:
                    print("SELL_STOP price reached")

        #toc = time.perf_counter()
        #print(f"Time taken: {toc - tic:0.4f} seconds")


# Function to add a new order
def new_order(order_dataframe, new_order, project_settings=[]):
    #balance = project_settings['backtest']['start_balance']
    #leverage = project_settings['backtest']['leverage']
    #balance_risk = project_settings['backtest']['balance_risk']

    # Update status of new_order dataframe
    new_order['status'] = "order"
    # Append to order_dataframe
    order_dataframe = pandas.concat([order_dataframe, new_order])
    return order_dataframe


