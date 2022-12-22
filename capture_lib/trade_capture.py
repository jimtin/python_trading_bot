from metatrader_lib import mt5_interaction
from sql_lib import sql_interaction


# Function to capture order actions
def capture_order(order_type, strategy, exchange, symbol, comment, project_settings,volume=0.0, stop_loss=0.0,
                  take_profit=0.0, price=None, paper=True, order_number=""):
    """
    Function to capture an order
    :param order_type: String
    :param strategy: String
    :param exchange: String
    :param symbol: String
    :param comment: String
    :param project_settings: JSON Object
    :param volume: Float
    :param stop_loss: Float
    :param take_profit: Float
    :param price: Float
    :param paper: Bool
    :param order_number: INT
    :return:
    """
    # Format objects correctly
    strategy = str(strategy)
    order_type = str(order_type)
    exchange = str(exchange)
    symbol = str(symbol)
    volume = float(volume)
    stop_loss = float(stop_loss)
    take_profit = float(take_profit)
    comment = str(comment)
    # Create the Database Object
    db_object = {
        "strategy": strategy,
        "exchange": exchange,
        "trade_type": order_type,
        "trade_stage": "order",
        "symbol": symbol,
        "volume": volume,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "comment": comment
    }

    # Check the price. If order_type == "BUY_STOP" or "SELL_STOP", price cannot be None
    if order_type == "BUY_STOP" or order_type == "SELL_STOP":
        if volume <= 0:
            print(f"Volume must be greater than 0 for an order type of {order_type}")
            raise SyntaxError # Use Pythons built in error for incorrect syntax
        if take_profit <= 0:
            print(f"Take Profit must be greater than 0 for an order type of {order_type}")
            raise ValueError  # Use Pythons built in error for incorrect value
        if stop_loss <= 0:
            print(f"Stop Loss must be greater than 0 for an order type of {order_type}")
            raise ValueError  # Use Pythons built in error for incorrect value
        if price == None:
            print(f"Price cannot be NONE on order_type {order_type}")
            raise ValueError  # Use Pythons built in error for incorrect value
        else:
            # Format price correctly
            price = float(price)
            # Add to database object
            db_object['price'] = price

    # If order_type == "BUY" or "SELL", price must be None
    if order_type == "BUY" or order_type == "SELL":
        if volume <= 0:
            print(f"Volume must be greater than 0 for an order type of {order_type}")
            raise ValueError  # Use Pythons built in error for incorrect value
        if take_profit <= 0:
            print(f"Take Profit must be greater than 0 for an order type of {order_type}")
            raise ValueError  # Use Pythons built in error for incorrect value
        if stop_loss <= 0:
            print(f"Stop Loss must be greater than 0 for an order type of {order_type}")
            raise ValueError  # Use Pythons built in error for incorrect value
        if price != None:
            print(f"Price must be NONE for order_type {order_type}")
            raise ValueError  # Use Pythons built in error for incorrect value
        else:
            # Make price = 0
            price = 0
            db_object['price'] = price

    # If order_type == "cancel", pass straight through into cancel order function
    if order_type == "CANCEL":
        # todo: fix this as it is incorrect. These values should come from what is passed to function
        db_object['price'] = 0
        db_object['volume'] = 0
        db_object['take_profit'] = 0
        db_object['stop_loss'] = 0
        # Branch based upon exchange
        if exchange == "mt5":
            # todo: Implement this within a Try statement
            order_outcome = mt5_interaction.cancel_order(order_number=order_number)
            if order_outcome is True:
                db_object['status'] = "cancelled"
                db_object['order_id'] = order_number
            # todo: an error should be raised if order outcome is not True
    # Place order based upon exchange
    else:
        if exchange == "mt5":
            # todo: this should be implemented inside a try statement
            db_object["order_id"] = mt5_interaction.place_order(
                order_type=order_type,
                symbol=symbol,
                volume=volume,
                stop_loss=stop_loss,
                take_profit=take_profit,
                comment=comment,
                price=price
            )
            # Update the status
            db_object["status"] = "placed"

    # Store in correct table
    if paper:
        sql_interaction.insert_paper_trade_action(trade_information=db_object, project_settings=project_settings)
        return True
    else:
        sql_interaction.insert_live_trade_action(trade_information=db_object, project_settings=project_settings)
        return True


# Function to capture modifications to open positions
def capture_position_update(trade_type, order_number, symbol, strategy, exchange, project_settings, comment,
                            new_stop_loss, new_take_profit, price, paper=True, volume=0.0):

    # Format the provided items correctly
    order_type = str(trade_type)
    order_number = int(order_number)
    symbol = str(symbol)
    new_stop_loss = float(new_stop_loss)
    new_take_profit = float(new_take_profit)
    strategy = str(strategy)
    exchange = str(exchange)

    # Create the db_object
    db_object = {
        "strategy": strategy,
        "exchange": exchange,
        "trade_type": order_type,
        "trade_stage": "order",
        "symbol": symbol,
        "volume": volume,
        "stop_loss": new_stop_loss,
        "take_profit": new_take_profit,
        "comment": comment,
        "price": price,
        "order_id": order_number
    }

    # Branch based upon trade_type
    if trade_type == "trailing_stop_update" or trade_type == "take_profit_update":
        # Branch again based upon exchange type
        if exchange == "mt5":
            # Use the modify_position function from mt5_interaction
            # todo: implement inside a try statement
            position_outcome = mt5_interaction.modify_position(
                order_number=order_number,
                symbol=symbol,
                new_stop_loss=new_stop_loss,
                new_take_profit=new_take_profit
            )
            # Update DB Object
            db_object['status'] = "position_modified"
    elif trade_type == "SELL" or trade_type == "BUY":
        # Branch again based upon exchange type
        if exchange == "mt5":
            # Use the close_position function from mt5_interaction
            #todo: implement inside a try statement
            position_outcome = mt5_interaction.close_position(
                order_number=order_number,
                symbol=symbol,
                volume=volume,
                order_type=trade_type,
                price=price,
                comment=comment
            )
            db_object['status'] = "position_modified"
    elif trade_type == "position":
        # Update the position only
        db_object['status'] = "position"


    # Update SQL
    # Branch based upon the table
    if paper:
        sql_interaction.insert_paper_trade_action(trade_information=db_object, project_settings=project_settings)
        return True
    else:
        sql_interaction.insert_live_trade_action(trade_information=db_object, project_settings=project_settings)
        return True

