import pandas
import time
from sql_lib import sql_interaction

trade_object = {}


# Function to backtest a strategy
def backtest(valid_trades_dataframe, time_orders_valid, tick_data_table_name, trade_table_name, project_settings,
             strategy, symbol):
    print("Starting Backtest script")
    # Make sure that SettingWithCopyWarning suppressed
    pandas.options.mode.chained_assignment = None
    # todo: Save the valid trades into a postgres table
    # todo: Sort valid_trades_dataframe by time
    # Add status of pending to orders
    valid_trades_dataframe['status'] = "pending"
    valid_trades_dataframe['time_valid'] = valid_trades_dataframe['time'] + time_orders_valid
    # Setup open_orders
    open_orders = pandas.DataFrame()
    # Setup open positions
    open_buy_positions = pandas.DataFrame()
    open_sell_positions = pandas.DataFrame()
    # Setup closed
    print("Data retrieved, analysis starting")
    # Query SQL in chunks
    # Create connection
    conn = sql_interaction.postgres_connect(project_settings)
    # Set up the trading object
    trade_object["backtest_settings"] = project_settings["backtest_settings"]
    trade_object["current_available_balance"] = trade_object["backtest_settings"]["test_balance"]
    trade_object["current_equity"] = 0
    trade_object["current_profit"] = 0
    trade_object["trade_table_name"] = trade_table_name
    trade_object["strategy"] = strategy
    trade_object["symbol"] = symbol
    # Create the trade table
    try:
        sql_interaction.create_mt5_backtest_trade_table(table_name=trade_table_name, project_settings=project_settings)
    except Exception as e:
        print(f"Error creating backtest trade table. {e}")
    with conn.cursor(name="backtest_cursor") as cursor:
        cursor.itersize = 100000
        query = f"SELECT * FROM {tick_data_table_name} ORDER BY time_msc;"
        cursor.execute(query)
        tic = time.perf_counter()
        for raw_row in cursor:
            # Turn row into a dictionary
            row = {
                "index": raw_row[0],
                "symbol": raw_row[1],
                "time": raw_row[2],
                "bid": raw_row[3],
                "ask": raw_row[4],
                "spread": raw_row[5],
                "last": raw_row[6],
                "volume": raw_row[7],
                "flags": raw_row[8],
                "volume_real": raw_row[9],
                "time_msc": raw_row[10],
                "human_time": raw_row[11],
                "human_time_msc": raw_row[12]
            }
            # Format time_msc into the milliseconds it should be
            row['time_msc'] = row['time_msc'] / 1000
            # Convert into a dictionary
            # Step 1: Check for orders which have become valid
            mask = (valid_trades_dataframe['time'] < row['time_msc'])
            if len(valid_trades_dataframe[mask]) > 0:
                # Retrieve the valid order
                new_data_frame = valid_trades_dataframe[mask]
                # Update status
                open_orders = new_order(
                    order_dataframe=open_orders,
                    new_order=new_data_frame,
                    row=row,
                    project_settings=project_settings
                )
                # Drop from valid trades dataframe
                valid_trades_dataframe = valid_trades_dataframe.drop(valid_trades_dataframe[mask].index)
            # Step 2: Check open orders for those which are no longer valid or have reached STOP PRICE
            if len(open_orders) > 0:
                # Check open orders for those which have expired
                mask = (open_orders['time_valid'] < row['time_msc'])
                if len(open_orders[mask]) > 0:
                    open_orders = expire_order(
                        order_dataframe=open_orders,
                        expired_order=open_orders[mask],
                        row=row,
                        project_settings=project_settings
                    )
                # Check if BUY_STOP reached
                mask = (open_orders['order_type'] == "BUY_STOP") & (open_orders['stop_price'] >= row['bid'])
                if len(open_orders[mask]) > 0:
                    # Add to Open Buy Positions
                    open_buy_positions = new_position(
                        position_dataframe=open_buy_positions,
                        new_position=open_orders[mask],
                        row=row,
                        project_settings=project_settings
                    )
                    # Drop from open orders as now a position
                    open_orders = open_orders.drop(open_orders[mask].index)
                # Check if SELL_STOP reached
                mask = (open_orders['order_type'] == "SELL_STOP") & (open_orders['stop_price'] <= row['bid'])
                if len(open_orders[mask]) > 0:
                    # Add to open_sell_positions
                    open_sell_positions = new_position(
                        position_dataframe=open_sell_positions,
                        new_position=open_orders[mask],
                        row=row,
                        project_settings=project_settings
                    )
                    open_orders = open_orders.drop(open_orders[mask].index)
            # Step 3: Check open positions to check their progress
            # Check open buy positions
            if len(open_buy_positions) > 0:
                # Check if any open buy positions have reached their TAKE_PROFIT
                mask = (open_buy_positions['take_profit'] <= row['bid'])
                if len(open_buy_positions[mask]) > 0:
                    # Todo: Add function with SQL to track
                    open_buy_positions = buy_take_profit_reached(
                        position_dataframe=open_buy_positions,
                        position=open_buy_positions[mask],
                        row=row,
                        project_settings=project_settings
                    )
                # Check if any open buy positions have reached their STOP_LOSS
                mask = (open_buy_positions['stop_loss'] >= row['bid'])
                if len(open_buy_positions[mask]) > 0:
                    # Todo: Add function with SQL to track
                    open_buy_positions = buy_take_profit_reached(
                        position_dataframe=open_buy_positions,
                        position=open_buy_positions[mask],
                        row=row,
                        project_settings=project_settings
                    )
            # Check open sell positions
            if len(open_sell_positions) > 0:
                # Check if any open sell positions have reached their TAKE_PROFIT
                mask = (open_sell_positions['take_profit'] >= row['bid'])
                if len(open_sell_positions[mask]) > 0:
                    # Todo: Add function with SQL to track
                    open_sell_positions = sell_take_profit_reached(
                        position_dataframe=open_sell_positions,
                        position=open_sell_positions[mask],
                        row=row,
                        project_settings=project_settings
                    )
                # Check if any open sell positions have reached a stop loss
                mask = (open_sell_positions['stop_loss'] <= row['bid'])
                if len(open_sell_positions[mask]) > 0:
                    open_sell_positions = sell_take_profit_reached(
                        position_dataframe=open_sell_positions,
                        position=open_sell_positions[mask],
                        row=row,
                        project_settings=project_settings
                    )
        toc = time.perf_counter()
        print(f"Time taken: {toc - tic:0.4f} seconds")


# Function to add a new order
def new_order(order_dataframe, new_order, row, project_settings=[]):
    # Iterate through the order dataframe
    for order in new_order.iterrows():
        order_id = order[0]
        order_details = order[1]
        # Calculate the amount risked, along with purchase
        risk = calc_risk_to_dollars()
        # Subtract the amount risked from the available balance as it's no longer available
        trade_object['current_available_balance'] = trade_object['current_available_balance'] - risk['risk_amount']
        # Add the amount risked to the current equity
        trade_object['current_equity'] = trade_object['current_equity'] + risk['risk_amount']
        print(f"Order Became valid. Balance: {trade_object['current_available_balance']}, "
              f"Equity: {trade_object['current_equity']}, Current Profit: {trade_object['current_profit']}")
        sql_interaction.insert_order_update(
            update_time=row["time_msc"],
            trade_type=order_details["order_type"],
            stop_loss=order_details["stop_loss"],
            take_profit=order_details["take_profit"],
            price=order_details["stop_price"],
            order_id=order_id,
            trade_object=trade_object,
            project_settings=project_settings,
            status="order"
        )
        new_order['amount_risked'] = risk['risk_amount']
    # Update status of new_order dataframe
    new_order['status'] = "order"
    # Append to order_dataframe
    order_dataframe = pandas.concat([order_dataframe, new_order])
    return order_dataframe


# Function to expire an order
def expire_order(order_dataframe, expired_order, row, trade_object, project_settings=[]):
    for order in expired_order.iterrows():
        order_id = order[0]
        order_details = order[1]
        # todo: Update balance etc
        print(row)
        sql_interaction.insert_order_update(
            update_time=row["time_msc"],
            trade_type=order_details["order_type"],
            stop_loss=order_details["stop_loss"],
            take_profit=order_details["take_profit"],
            price=order_details["stop_price"],
            order_id=order_id,
            trade_object=trade_object,
            project_settings=project_settings,
            status="expired"
        )
    # Update status of expired_order
    expired_order['status'] = "expired"
    # Drop from order_dataframe
    updated_order_dataframe = order_dataframe.drop(expired_order.index)
    print(f"Order expired {expired_order.index} at {row['time_msc']}")
    # Return updated order dataframe
    return updated_order_dataframe


# Function to add a new position
def new_position(position_dataframe, new_position, row, project_settings):
    # todo: Update SQL Table with outcome
    # todo: Update volume with quantity purchased
    for position in new_position.iterrows():
        position_id = position[0]
        position_details = position[1]
        print(f"Order {position_id} became a position at price {row['bid']}")
        # No change to balance or equity as already covered in the order
        sql_interaction.insert_new_position(
            trade_type=position_details['order_type'],
            status="position",
            stop_loss=position_details['stop_loss'],
            take_profit=position_details['take_profit'],
            price=row['bid'],
            order_id=position_id,
            trade_object=trade_object,
            update_time=row['time_msc'],
            project_settings=project_settings,
            qty_purchased=position_details['amount_risked']
        )

    # Update status of order
    new_position['status'] = "position"
    # Append to position dataframe
    position_dataframe = pandas.concat([position_dataframe, new_position])
    return position_dataframe


# Function when a BUY Take Profit Reached
def buy_take_profit_reached(position_dataframe, position, row, project_settings):
    # todo: Update SQL Table with outcome
    # Query SQL to find what the most recent price take profit was (make future compatible with trailing stop)
    for pos_tp in position.iterrows():
        last_trade = sql_interaction.retrieve_last_position(
            order_id=pos_tp[0],
            trade_object=trade_object,
            project_settings=project_settings
        )
        print("BUY TAKE PROFIT DETAILS")
        print(last_trade)
    # Update status of position
    position['status'] = "closed"
    print(f"BUY Take Profit Reached. Price: {row['bid']}. ID: {position.index}. Time: {row['time_msc']}")
    # Remove from position dataframe
    position_dataframe = position_dataframe.drop(position.index)
    return position_dataframe


# Function when a BUY Stop Loss reached
def buy_stop_loss_reached(position_dataframe, position, row, project_settings):
    # todo: Update SQL Table with outcome
    for pos_sl in position.iterrows():
        last_trade = sql_interaction.retrieve_last_position(
            order_id=pos_sl[0],
            trade_object=trade_object,
            project_settings=project_settings
        )
    # Update status of position
    position['status'] = "closed"
    print(f"BUY Stop Loss Reached. Price: {row['bid']}. ID: {position.index}. Time: {row['time_msc']}")
    position_dataframe = position_dataframe.drop(position.index)
    return position_dataframe


# Function when a SELL Take Profit reached
def sell_take_profit_reached(position_dataframe, position, row, project_settings):
    # todo: Update SQL Table with outcome
    for pos_tp in position.iterrows():
        last_trade = sql_interaction.retrieve_last_position(
            order_id=pos_tp[0],
            trade_object=trade_object,
            project_settings=project_settings
        )
    # Update status of position
    position['status'] = 'closed'
    print(f"SELL Stop Loss Reached. Price: {row['bid']}. ID: {position.index}. Time: {row['time_msc']}")
    position_dataframe = position_dataframe.drop(position.index)
    return position_dataframe


# Function when a SELL Stop Loss reached
def sell_stop_loss_reached(position_dataframe, position, row, project_settings):
    # todo: Update SQL Table with outcome
    for pos_sl in position.iterrows():
        last_trade = sql_interaction.retrieve_last_position(
            order_id=pos_sl[0],
            trade_object=trade_object,
            project_settings=project_settings
        )
        print("SELL LAST TRADE")
        print(last_trade)
    # Update status of position
    position['status'] = "closed"
    print(f"SELL Stop Loss Reached. Price: {row['bid']}. ID: {position.index}. Time: {row['time_msc']}")
    position_dataframe = position_dataframe.drop(position.index)
    return position_dataframe


def calc_risk_to_dollars():
    # Setup the trade settings
    purchase_dollars = {
        "risk_amount": 0.00
    }
    if trade_object["backtest_settings"]["compounding"] == "true":
        risk_amount = trade_object["current_available_balance"] * \
                      trade_object["backtest_settings"]["risk_percent"] / 100
    else:
        risk_amount = trade_object["backtest_settings"]["test_balance"] * \
                      trade_object["backtest_settings"]["risk_percent"] / 100
    # Save to variable
    purchase_dollars["risk_amount"] = risk_amount
    # Multiply by the leverage
    purchase_dollars["purchase_total"] = risk_amount * trade_object["backtest_settings"]["leverage"]
    return purchase_dollars
