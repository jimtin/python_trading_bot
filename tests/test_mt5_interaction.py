import pytest
import exceptions
import os
import json

# Libraries being tested
import main
from metatrader_lib import mt5_interaction

# Define project settings location
import_filepath = "test_settings.json"

fake_login_details = {
    "username": 00000000,
    "password": "password",
    "server": "Test_Server",
    "path": "C:/MetaTrader5/terminal64.exe"
}


def test_start_mt5_fail():
    # Test an exception raised for unable to login
    with pytest.raises(exceptions.MetaTraderInitializeError) as e:
        mt5_interaction.start_mt5(
            username=fake_login_details["username"],
            password=fake_login_details["password"],
            server=fake_login_details["server"],
            path=fake_login_details["path"]
        )
        assert e.type == exceptions.MetaTraderInitializeError


def test_start_mt5_succeed():
    # Test that function passed when correct login details provided
    real_login_details = main.get_project_settings(import_filepath)
    real_login_details = real_login_details["mt5"]["paper"]
    value = mt5_interaction.start_mt5(
        username=real_login_details["username"],
        password=real_login_details["password"],
        server=real_login_details["server"],
        path=real_login_details["mt5Pathway"]
    )
    assert value is True


# Test a fake symbol not enabled
def test_initialize_symbols_fake():
    # Fake Symbol
    fake_symbol = ["HEYHEY"]
    with pytest.raises(exceptions.MetaTraderSymbolDoesNotExistError) as e:
        mt5_interaction.initialize_symbols(fake_symbol)
        assert e.type == exceptions.MetaTraderSymbolDoesNotExistError


# Test a real symbol enabled
def test_initialize_symbols_real():
    # Real Symbol
    real_symbol = ["BTCUSD.a"]
    value = mt5_interaction.initialize_symbols(real_symbol)
    assert value is True


# Test that place order does not accept invalid order types
def test_place_order_wrong_order_type():
    # Fake order
    with pytest.raises(SyntaxError) as e:
        mt5_interaction.place_order("WRONG_TYPE", "BTCUSD.a", 0.0, 0.0,0.0,"comment")
        assert e.type == SyntaxError


# Test that place_order throws an error if a balance which is too large is placed
def test_place_order_incorrect_balance():
    # Get the options for a test order
    test_order = get_a_test_order()
    with pytest.raises(exceptions.MetaTraderOrderCheckError) as e:
        mt5_interaction.place_order("BUY", "BTCUSD.a", test_order['incorrect_volume'], test_order['buy_stop_loss'],
                                    test_order['buy_take_profit'], "UnitTestOrder")
        assert e.type == exceptions.MetaTraderOrderCheckError

# Test that place_order throws an error if incorrect stop_loss
def test_place_order_incorrect_stop_loss():
    # Get options for a test order
    test_order = get_a_test_order()
    with pytest.raises(exceptions.MetaTraderOrderPlacingError) as e:
        mt5_interaction.place_order(
            order_type="BUY",
            symbol="BTCUSD.a",
            volume=test_order['correct_volume'],
            stop_loss=test_order['sell_stop_loss'],
            take_profit=test_order['buy_take_profit'],
            comment="TestTrade"
        )
        assert e.type == exceptions.MetaTraderOrderPlacingError


# Test that place_order throws an error if incorrect take_profit
def test_place_order_incorrect_take_profit():
    test_order = get_a_test_order()
    with pytest.raises(exceptions.MetaTraderOrderPlacingError) as e:
        mt5_interaction.place_order(
            order_type="BUY",
            symbol="BTCUSD.a",
            volume=test_order['correct_volume'],
            stop_loss=test_order['buy_stop_loss'],
            take_profit=test_order['sell_take_profit'],
            comment="TestTrade"
        )
        assert e.type == exceptions.MetaTraderOrderPlacingError


# Test that error thrown if price == 0 for SELL_STOP
def test_place_order_incorrect_sell_stop():
    test_order = get_a_test_order()
    with pytest.raises(exceptions.MetaTraderIncorrectStopPriceError) as e:
        mt5_interaction.place_order(
            order_type="SELL_STOP",
            symbol="BTCUSD.a",
            volume=test_order['correct_volume'],
            stop_loss=test_order['sell_stop_loss'],
            take_profit=test_order['sell_take_profit'],
            comment="TestTrade"
        )
        assert e.type == exceptions.MetaTraderIncorrectStopPriceError


# Test that error thrown if price == 0 for BUY_STOP
def test_place_order_incorrect_buy_stop():
    test_order = get_a_test_order()
    with pytest.raises(exceptions.MetaTraderIncorrectStopPriceError) as e:
        mt5_interaction.place_order(
            order_type="BUY_STOP",
            symbol="BTCUSD.a",
            volume=test_order['correct_volume'],
            stop_loss=test_order['buy_stop_loss'],
            take_profit=test_order['buy_take_profit'],
            comment="TestTrade"
        )
        assert e.type == exceptions.MetaTraderIncorrectStopPriceError


# Test that placing a BUY order works
def test_place_order_buy():
    # Get options for a test order
    test_order = get_a_test_order()
    outcome = mt5_interaction.place_order(
            order_type="BUY",
            symbol="BTCUSD.a",
            volume=test_order['correct_volume'],
            stop_loss=test_order['buy_stop_loss'],
            take_profit=test_order['buy_take_profit'],
            comment="TestTrade"
        )
    assert outcome == None


# Test that placing SELL order works
def test_place_order_sell():
    test_order = get_a_test_order()
    outcome = mt5_interaction.place_order(
        order_type="SELL",
        symbol="BTCUSD.a",
        volume=test_order['correct_volume'],
        stop_loss=test_order['sell_stop_loss'],
        take_profit=test_order['sell_take_profit'],
        comment="TestTrade"
    )
    assert outcome == None


# Test that placing a BUY_STOP order works
def test_place_order_buy_stop():
    test_order = get_a_test_order()
    outcome = mt5_interaction.place_order(
        order_type="BUY_STOP",
        symbol="BTCUSD.a",
        volume=test_order['correct_volume'],
        stop_loss=test_order['buy_stop_loss'],
        take_profit=test_order['buy_take_profit'],
        comment="TestTrade",
        price=test_order['correct_buy_stop']
    )
    assert outcome == None


# Test that placing a SELL_STOP order works
def test_place_order_sell_stop():
    test_order = get_a_test_order()
    outcome = mt5_interaction.place_order(
        order_type="SELL_STOP",
        symbol="BTCUSD.a",
        volume=test_order['correct_volume'],
        stop_loss=test_order['sell_stop_loss'],
        take_profit=test_order['sell_take_profit'],
        comment="TestTrade",
        price=test_order['correct_sell_stop']
    )
    assert outcome == None


# Test that canceling a non-existing order throws an error
def test_cancel_order_incorrect():
    order_number = 12345678
    with pytest.raises(exceptions.MetaTraderCancelOrderError) as e:
        mt5_interaction.cancel_order(order_number)
        assert e.type == exceptions.MetaTraderCancelOrderError


# Test the ability to cancel an order
def test_cancel_order():
    # Retrieve a list of orders
    orders = mt5_interaction.get_open_orders()
    # Iterate through and cancel
    for order in orders:
        outcome = mt5_interaction.cancel_order(order)
        assert outcome == True


# Test the ability to modify an open positions stop loss
def test_modify_position_new_stop_loss():
    # Retrieve a list of current positions
    positions = mt5_interaction.get_open_positions()
    # Modify the stop loss of positions with comment "TestTrade"
    for position in positions:
        if position[17] == "TestTrade":
            # Add $100 to stop loss, then modify
            new_stop_loss = position[11] + 100
            outcome = mt5_interaction.modify_position(
                order_number=position[0],
                symbol=position[16],
                new_stop_loss=new_stop_loss,
                new_take_profit=position[12]
            )
            assert outcome == True


# Test ability to modify an open positions take profit
def test_modify_position_new_take_profit():
    # Retrieve a list of current positions
    positions = mt5_interaction.get_open_positions()
    # Modify the take profit of positions with the comment "TestTrade"
    for position in positions:
        if position[17] == "TestTrade":
            # Add $100 to take profit, then modify
            new_take_profit = position[12] + 100
            outcome = mt5_interaction.modify_position(
                order_number=position[0],
                symbol=position[16],
                new_stop_loss=position[11],
                new_take_profit=new_take_profit
            )
            assert outcome == True


# Test ability to modify both take profit and stop loss simultaneously
def test_modify_position():
    # Retrieve a list of current positions
    positions = mt5_interaction.get_open_positions()
    # Modify the both take profit and stop loss positions with the comment "TestTrade"
    for position in positions:
        if position[17] == "TestTrade":
            # Subtract $100 to take profit, then modify
            new_take_profit = position[12] - 100
            new_stop_loss = position[11] - 100
            outcome = mt5_interaction.modify_position(
                order_number=position[0],
                symbol=position[16],
                new_stop_loss=new_stop_loss,
                new_take_profit=new_take_profit
            )
            assert outcome == True

# Test Modify Position throws an error
def test_modify_position_error():
    # Retrieve a list of current positions
    positions = mt5_interaction.get_open_positions()
    for position in positions:
        if position[17] == "TestTrade":
            with pytest.raises(exceptions.MetaTraderModifyPositionError) as e:
                mt5_interaction.modify_position(
                    order_number=12345678,
                    symbol=position[16],
                    new_stop_loss=position[11],
                    new_take_profit=position[12]
                )
                assert e.type == exceptions.MetaTraderCancelOrderError


# Test function to close a position
def test_close_position_syntax():
    # Retrieve a list of current positions
    positions = mt5_interaction.get_open_positions()
    for position in positions:
        if position[17] == "TestTrade":
            with pytest.raises(SyntaxError) as e:
                mt5_interaction.close_position(
                    order_number=position[0],
                    symbol=position[16],
                    volume=position[9],
                    order_type=position[5],
                    price=position[13],
                    comment="TestTrade"
                )
                assert e.type == SyntaxError


# Test function to attempt to close a position with a bogus order_number
def test_close_position_wrong_order_number():
    # Retrieve a list of current positions
    positions = mt5_interaction.get_open_positions()
    for position in positions:
        if position[17] == "TestTrade":
            with pytest.raises(exceptions.MetaTraderClosePositionError) as e:
                if position[5] == 0:
                    order_type = "SELL"
                elif position[5] == 1:
                    order_type = "BUY"
                mt5_interaction.close_position(
                    order_number=12345678,
                    symbol=position[16],
                    volume=position[9],
                    order_type=order_type,
                    price=position[13],
                    comment="TestTrade"
                )


# Test the close position function works
def test_close_position():
    # Retreive a list of current positions
    positions = mt5_interaction.get_open_positions()
    for position in positions:
        if position[17] == "TestTrade":
            if position[5] == 0:
                order_type = "SELL"
            elif position[5] == 1:
                order_type = "BUY"
            outcome = mt5_interaction.close_position(
                    order_number=position[0],
                    symbol=position[16],
                    volume=position[9],
                    order_type=order_type,
                    price=position[13],
                    comment="TestTrade"
                )
            assert outcome == True


### Complex test
def test_fractional_close():
    # Step 1: Make a trade with a volume of 0.2
    # Retrieve details for a test order
    test_order = get_a_test_order()
    # Update volume
    test_order['correct_volume'] = 0.2
    # Place a BUY order
    buy_order = mt5_interaction.place_order(
        order_type="BUY",
        symbol="BTCUSD.a",
        volume=test_order['correct_volume'],
        stop_loss=test_order['buy_stop_loss'],
        take_profit=test_order['buy_take_profit'],
        comment="ComplexTestOrder"
    )
    # Retrieve a list of current positions
    positions = mt5_interaction.get_open_positions()
    for position in positions:
        if position[17] == "ComplexTestOrder":
            # Get 50% of volume
            volume = position[9] / 2
            # Get price less 100
            price = position[13] - 100
            sell_order = mt5_interaction.close_position(
                order_number=position[0],
                symbol=position[16],
                volume=volume,
                order_type="SELL",
                price=price,
                comment="ComplexTestOrderSell"
            )
            assert sell_order == True

    # Now fully close out the positions to complete
    positions = mt5_interaction.get_open_positions()
    for position in positions:
        if position[17] == "ComplexTestOrder":
            sell_order = mt5_interaction.close_position(
                order_number=position[0],
                symbol=position[16],
                volume=position[9],
                order_type="SELL",
                price=position[13]-100,
                comment="ComplexTestOrderSell"
            )
            assert sell_order == True



### Helper functions
def get_a_test_order():
    # Get the current BTCUSD.a price, Assume balance is not more than $100,000
    current_price = mt5_interaction.retrieve_latest_tick("BTCUSD.a")['ask']
    return_object = {
        "current_price": current_price,
        "correct_buy": current_price,
        "incorrect_buy": current_price - 1000,
        "buy_stop_loss": current_price - 2000,
        "sell_stop_loss": current_price + 2000,
        "buy_take_profit": current_price + 2000,
        "sell_take_profit": current_price - 2000,
        "correct_buy_stop": current_price + 1000,
        "incorrect_buy_stop": current_price - 1000,
        "correct_sell_stop": current_price - 1000,
        "incorrect_sell_stop": current_price + 1000,
        "incorrect_volume": (100000 / float(current_price)) + 1,
        "correct_volume": 0.1
    }
    return return_object

