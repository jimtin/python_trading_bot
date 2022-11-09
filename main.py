import json
import os
from coinbase_lib import get_account_details, get_candlesticks
from indicators import bullish_engulfing, bearish_engulfing


# Variable for the location of settings.json
import_filepath = "settings.json"


# Function to import settings from settings.json
def get_project_settings(importFilepath):
    # Test the filepath to sure it exists
    if os.path.exists(importFilepath):
        # Open the file
        f = open(importFilepath, "r")
        # Get the information from file
        project_settings = json.load(f)
        # Close the file
        f.close()
        # Return project settings to program
        return project_settings
    else:
        return ImportError

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Import project settings
    project_settings = get_project_settings(import_filepath)
    # Retrieve the account details
    # account_details = get_account_details.get_account_details(project_settings=project_settings)
    candlestick_data = get_candlesticks.get_candlestick_data("BTC-USDC", "D1")
    # Check Bullish Engulfing
    bullish_engulfing_check = bullish_engulfing.calc_bullish_engulfing(
        dataframe=candlestick_data,
        exchange="coinbase",
        project_settings=project_settings
    )
    print(f"Bullish Engulfing Check: {bullish_engulfing_check}")
    bearish_engulfing_check = bearish_engulfing.calc_bearish_engulfing(
        dataframe=candlestick_data,
        exchange="coinbase",
        project_settings=project_settings
    )
    print(f"Bearish Engulfing Check: {bearish_engulfing_check}")

