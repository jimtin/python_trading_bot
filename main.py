import json
import os
from metatrader_lib import mt5_interaction
import pandas as pd
import display_lib
from sql_lib import sql_interaction
from strategies import ema_cross
from backtest_lib import backtest, setup_backtest, backtest_analysis
import argparse
from indicator_lib import calc_all_indicators, doji_star, rsi
import datetime

# Variable for the location of settings.json
import_filepath = "settings.json"

# Global settings
global exchange
global explore


# Function to import settings from settings.json
def get_project_settings(import_filepath):
    """
    Function to import settings from settings.json
    :param import_filepath: string to the location of settings.json
    :return: JSON object with project settings
    """
    # Test the filepath to sure it exists
    if not os.path.exists(import_filepath):
        raise ImportError

    with open(import_filepath) as f:
        project_settings = json.load(f)

    return project_settings


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

    return True


def add_arguments(parser):
    """
    Function to add arguments to the parser
    :param parser: parser object
    :return: updated parser object
    """
    # Add Options
    parser.add_argument("-e", "--Explore", help="Use this to explore the data", action="store_true")
    parser.add_argument("-d", "--Display", help="Use this to display the data", action="store_true")
    parser.add_argument("-a", "--all_indicators", help="Select all indicator_lib", action="store_true")
    parser.add_argument("--doji_star", help="Select doji star indicator to be calculated", action="store_true")
    parser.add_argument("--rsi", help="Select RSI indicator to be calculated", action="store_true")
    parser.add_argument("-x", "--Exchange", help="Set which exchange you will be using")
    parser.add_argument("--symbol", help="Use this to use a custom symbol with the Explore option")
    parser.add_argument("-t", "--timeframe", help="Select a timeframe to explore data")
    return parser


def parse_arguments(args_parser_variable):
    """
    Function to parse provided arguments and improve from there
    :param args_parser_variable:
    :return: True when completed
    """
    # Check if data exploration selected
    if args_parser_variable.Explore:
        print("Data exploration selected")
        # Check for exchange
        if not args_parser_variable.Exchange:
            print("No exchange selected")
            raise SystemExit(1)

        if args_parser_variable.Exchange == "metatrader":
            global exchange
            exchange = "mt5"
        print(f"Exchange selected: {exchange}")

        # Check for Timeframe
        if args_parser_variable.timeframe:
            print(f"Timeframe selected: {args_parser_variable.timeframe}")
        else:
            print("No timeframe selected")
            raise SystemExit(1)

        # Check for Symbol
        if not args_parser_variable.symbol:
            print("No symbol selected")
            raise SystemExit(1)

        print(f"Symbol selected: {args_parser_variable.symbol}")
        return True

    return False


def manage_exploration(args):
    """
    Function to manage data exploration when --Explore option selected
    :param args: system arguments
    :return: dataframe
    """
    if args.Exchange == "metatrader":
        # Retreive a large amount of data
        data = mt5_interaction.query_historic_data(
            symbol=args.symbol,
            timeframe=args.timeframe,
            number_of_candles=1000
        )
        data = pd.DataFrame(data)
        # Retrieve whatever indicator_lib have been selected
        # If all indicators selected, calculate all of them
        if args.all_indicators:
            print(f"All indicators selected. Calculation may take some time")
            indicator_dataframe = calc_all_indicators.all_indicators(dataframe=data)
            return indicator_dataframe
        else:
            if args.Display:  # construct the base figure
                # Add a column 'human_time' to the dataframe which converts the unix time to human readable
                data['human_time'] = data['time'].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
                fig = display_lib.construct_base_candlestick_graph(
                    dataframe=data,
                    candlestick_title=f"{args.symbol} {args.timeframe} Data Explorer"
                )

                # Check for doji_star
                if args.doji_star and args.Display:
                    print(f"Doji Star selected with display")
                    indicator_dataframe = doji_star.doji_star(
                        dataframe=data,
                        display=True,
                        fig=fig
                    )

                # Check for RSI
                if args.rsi:
                    print(f"RSI selected")
                    indicator_dataframe = rsi.rsi(
                        dataframe=data,
                        display=True,
                        fig=fig
                    )
            else:
                # Check for doji_star
                if args.doji_star:
                    print(f"Doji Star selected")
                    indicator_dataframe = doji_star.doji_star(
                        dataframe=data
                    )

                # Check for RSI
                if args.rsi:
                    print(f"RSI selected")
                    indicator_dataframe = rsi.rsi(
                        dataframe=data
                    )

            # If display is true, once all indicators have been calculated, display the figure
            if args.Display:
                print("Displaying data")
                display_lib.display_graph(
                    plotly_fig=fig,
                    graph_title=f"{args.symbol} {args.timeframe} Data Explorer",
                    dash=False
                )

        # Once all indicators have been calculated, return the dataframe
        return indicator_dataframe
    else:
        print("No exchange selected")
        raise SystemExit(1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    project_settings = get_project_settings(import_filepath=import_filepath)
    check_exchanges(project_settings)
    # Show all columns pandas
    pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # Setup arguments to the script
    parser = argparse.ArgumentParser()
    # Update with options
    parser = add_arguments(parser=parser)
    args = parser.parse_args()
    explore = parse_arguments(args_parser_variable=args)

    if explore:
        manage_exploration(args=args)
    else:
        data = manage_exploration(args=args)
        print(data)
