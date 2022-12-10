import json
import os
from metatrader_lib import mt5_interaction


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
    # Check Exchanges
    check_exchanges(project_settings=project_settings)
    # Place an order
    """
    mt5_interaction.place_order(
        order_type="BUY",
        symbol="BTCUSD.a",
        volume=0.1,
        stop_loss=17130.00,
        take_profit=17200.00,
        comment="Test Trade"
    )
    """
    mt5_interaction.close_position(
        order_number=12345678, # Replace with your order number
        symbol="BTCUSD.a", # Must match your place order symbol
        volume=0.1, # Volume must be <= purchase volume
        order_type="SELL", # Must be the opposite of the purchase
        price=17135.10, # Must be <= to current price
        comment="Test Trade"
    )


