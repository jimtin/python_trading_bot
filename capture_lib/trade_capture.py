from metatrader_lib import mt5_interaction
from sql_lib import sql_interaction
import exceptions


# Function to capture order actions
def capture_order(order_type, strategy, exchange, symbol, comment, project_settings, volume=0.0, stop_loss=0.0,
                  take_profit=0.0, price=None, paper=True, order_number="", backtest=False):
    """
    Function to capture an order
    """
    strategy = str(strategy)
    order_type = str(order_type)
    exchange = str(exchange)
    symbol = str(symbol)
    volume = float(volume)
    stop_loss = float(stop_loss)
    take_profit = float(take_profit)
    comment = str(comment)

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
            raise SyntaxError
        if take_profit <= 0:
            print(f"Take Profit must be greater than 0 for an order type of {order_type}")
            raise ValueError
        if stop_loss <= 0:
            print(f"Stop Loss must be greater than 0 for an order type of {order_type}")
            raise ValueError
        if price is None:
            print(f"Price cannot be NONE on order_type {order_type}")
            raise ValueError

        price = float(price)
        db_object['price'] = price

    # If order_type == "BUY" or "SELL", price must be None
    if order_type == "BUY" or order_type == "SELL":
        if volume <= 0:
            print(f"Volume must be greater than 0 for an order type of {order_type}")
            raise ValueError
        if take_profit <= 0:
            print(f"Take Profit must be greater than 0 for an order type of {order_type}")
            raise ValueError
        if stop_loss <= 0:
            print(f"Stop Loss must be greater than 0 for an order type of {order_type}")
            raise ValueError
        if price is not None:
            print(f"Price must be NONE for order_type {order_type}")
            raise ValueError

        price = 0
        db_object['price'] = price

    if not backtest:
        # If order_type == "cancel", pass straight through into cancel order function
        if order_type == "CANCEL":
            db_object['price'] = price
            db_object['volume'] = volume
            db_object['take_profit'] = take_profit
            db_object['stop_loss'] = stop_loss
            # Branch based upon exchange
            if exchange == "mt5":
                try:
                    order_outcome = mt5_interaction.cancel_order(order_number=order_number)
                    if order_outcome is True:
                        db_object['status'] = "cancelled"
                        db_object['order_id'] = order_number
                    else:
                        raise exceptions.MetaTraderCancelOrderError
                except Exception as e:
                    print(f"Exception cancelling order order on MT5. {e}")
        # Place order based upon exchange
        else:
            if exchange == "mt5":
                try:
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
                except Exception as e:
                    print(f"Exception placing ")

    # Store in correct table
    if backtest:
        return True

    if paper:
        sql_interaction.insert_paper_trade_action(trade_information=db_object, project_settings=project_settings)
        return True

    sql_interaction.insert_live_trade_action(trade_information=db_object, project_settings=project_settings)
    return True


# Function to capture modifications to open positions
def capture_position_update(trade_type, order_number, symbol, strategy, exchange, project_settings, comment,
                            new_stop_loss, new_take_profit, price, paper=True, volume=0.0):
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

    if trade_type in ["trailing_stop_update", "take_profit_update"]:
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
    elif trade_type in ["SELL", "BUY"]:
        # Branch again based upon exchange type
        if exchange == "mt5":
            # Use the close_position function from mt5_interaction
            # todo: implement inside a try statement
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
    if paper:
        sql_interaction.insert_paper_trade_action(trade_information=db_object, project_settings=project_settings)
    else:
        sql_interaction.insert_live_trade_action(trade_information=db_object, project_settings=project_settings)
    return True
