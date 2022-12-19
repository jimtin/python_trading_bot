import json
import os
from sql_lib import sql_interaction
from metatrader_lib import mt5_interaction
from capture_lib import trade_capture


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
        return PermissionError
    # Check MT5 Paper Trading
    mt5_paper_check = mt5_interaction.start_mt5(
        username=project_settings["mt5"]["paper"]["username"],
        password=project_settings["mt5"]["paper"]["password"],
        server=project_settings["mt5"]["paper"]["server"],
        path=project_settings["mt5"]["paper"]["mt5Pathway"],
    )
    if not mt5_paper_check:
        print("MT5 Paper Connection Error")
        return PermissionError

    # Return True if all steps pass
    return True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Import project settings
    project_settings = get_project_settings(import_filepath=import_filepath)
    # Check exchanges
    check_exchanges(project_settings)
    # Create a BUY order
    """
    trade_capture.capture_order(
        order_type="CANCEL",
        strategy="TestStrategy",
        exchange="mt5",
        symbol="BTCUSD.a",
        volume=0.1,
        stop_loss=16000.00,
        take_profit=17000.00,
        comment="TestOrder",
        paper=True,
        project_settings=project_settings,
        #price=16880.00
        order_number=311891382
    )
    """
    trade_capture.capture_position_update(
        trade_type="take_profit_update",
        order_number=311875716,
        symbol="BTCUSD.a",
        strategy="TestStrategy",
        exchange="mt5",
        project_settings=project_settings,
        comment="Test Strategy",
        new_stop_loss=16000.00,
        new_take_profit=17005.00,
        price=0.00,
        volume=0.00,
    )


