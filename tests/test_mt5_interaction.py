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


### Helper function
def get_a_test_order():
    # Get the current BTCUSD.a price, Assume balance is not more than $100,000
    current_price = mt5_interaction.retrieve_latest_tick("BTCUSD.a")['ask']
    return_object = {
        "current_price ": current_price,
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

