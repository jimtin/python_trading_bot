import json
import os
from metatrader_lib import mt5_interaction
import pandas
import display_lib
from sql_lib import sql_interaction
from strategies import ema_cross
from backtest_lib import backtest, setup_backtest

# Variable for the location of settings.json
import_filepath = "settings.json"


# Function to import settings from settings.json
def get_project_settings(import_filepath):
    """
    Function to import settings from settings.json
    :param import_filepath:
    :return: JSON object with project settings
    """
    # Test the filepath to sure it exists
    if os.path.exists(import_filepath):
        # Open the file
        f = open(import_filepath, "r")
        # Get the information from file
        project_settings = json.load(f)
        # Close the file
        f.close()
        # Return project settings to program
        return project_settings
    else:
        return ImportError


def check_exchanges(project_settings):
    """
    Function to check if exchanges are working
    :param project_settings:
    :return: Bool
    """
    # Check MT5 Live trading
    mt5_live_check = mt5_interaction.start_mt5(
        username=project_settings["mt5"]["live"]["username"],
        password=project_settings["mt5"]["live"]["password"],
        server=project_settings["mt5"]["live"]["server"],
        path=project_settings["mt5"]["live"]["mt5Pathway"],
    )
    if not mt5_live_check:
        print("MT5 Live Connection Error")
        raise PermissionError
    # Check MT5 Paper Trading
    mt5_paper_check = mt5_interaction.start_mt5(
        username=project_settings["mt5"]["paper"]["username"],
        password=project_settings["mt5"]["paper"]["password"],
        server=project_settings["mt5"]["paper"]["server"],
        path=project_settings["mt5"]["paper"]["mt5Pathway"],
    )
    if not mt5_paper_check:
        print("MT5 Paper Connection Error")
        raise PermissionError

    # Return True if all steps pass
    return True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Import project settings
    project_settings = get_project_settings(import_filepath=import_filepath)
    # Check exchanges
    check_exchanges(project_settings)
    # Show all columns pandas
    pandas.set_option('display.max_columns', None)
    #pandas.set_option('display.max_rows', None)

    # Dev code
    #setup_backtest.set_up_backtester("test_script", "blah", "month", project_settings)
    #display_lib.show_data("test_script_mt5_backtest_raw_candles", "", "BTC Explorer", project_settings)

    dataframe = sql_interaction.retrieve_dataframe("test_script_mt5_backtest_raw_candles", project_settings)
    trade_dataframe = ema_cross.ema_cross_strategy(dataframe, display=False, upload=False, project_settings=project_settings)
    backtest.backtest(
        valid_trades_dataframe=trade_dataframe,
        time_orders_valid=1800,
        tick_data_table_name="test_script_mt5_backtest_ticks",
        trade_table_name="test_script_mt5_backtest_trade_actions",
        project_settings=project_settings,
        strategy="test_strategy",
        symbol="BTCUSD.a",
        comment="initial_strategy"
    )

