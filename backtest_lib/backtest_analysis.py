from sql_lib import sql_interaction
import display_lib
import datetime
import pandas
from backtest_lib import setup_backtest, backtest
from strategies import ema_cross
import hashlib
import pytz


# Function to initiate and manage backtest
def do_backtest(strategy_name, symbol, candle_timeframe, test_timeframe, project_settings, get_data=True,
                exchange="mt5", optimize=False, display=False, variables={"risk_ratio": 3}, full_analysis=False,
                redo_analysis=False, regather_data=False):
    symbol_name = symbol.split(".")
    # Set the table names
    table_name_base = strategy_name + "_" + symbol_name[0] + "_"
    raw_data_table_name = f"{table_name_base}candles".lower()
    tick_data_table_name = f"{table_name_base}ticks".lower()
    trade_table_name = f"{table_name_base}trade_actions".lower()
    balance_tracker_table = f"{table_name_base}balance".lower()
    valid_trades_table = f"{table_name_base}trades".lower()
    var = str(variables)
    comment = hashlib.sha256(var.encode("utf-8"))
    comment = str(comment.hexdigest())
    # Make sure the summary table is created
    try:
        sql_interaction.create_summary_table(project_settings)
    except Exception as e:
        if e == 'relation "strategy_testing_outcomes" already exists':
            print("Failed to execute query: Strategy Testing Outcomes database ready")
        else:
            print(e)

    if regather_data:
        # todo: Delete previous data
        pass
    # If data required
    if get_data:
        print("Getting Data")
        # Set up backtest Postgres Tables and get raw data
        setup_backtest.set_up_backtester(
            strategy_name=strategy_name,
            symbol=symbol,
            candle_timeframe=candle_timeframe,
            backtest_timeframe=test_timeframe,
            project_settings=project_settings,
            exchange=exchange,
            candle_table_name=raw_data_table_name,
            tick_table_name=tick_data_table_name,
            balance_tracker_table=balance_tracker_table
        )
    if redo_analysis:
        # todo: Delete previous analysis tables
        pass
    if full_analysis:
        # Get the raw data
        raw_dataframe = sql_interaction.retrieve_dataframe(
            table_name=raw_data_table_name,
            project_settings=project_settings
        )
        # Construct the trades
        trades_dataframe = ema_cross.ema_cross_strategy(
            dataframe=raw_dataframe,
            risk_ratio=variables["risk_ratio"]
        )
        # Run the backtest
        backtest.backtest(
            valid_trades_dataframe=trades_dataframe,
            time_orders_valid=1800,
            tick_data_table_name=tick_data_table_name,
            trade_table_name=trade_table_name,
            project_settings=project_settings,
            strategy=strategy_name,
            symbol=symbol,
            comment=comment,
            balance_table=balance_tracker_table,
            valid_trades_table=valid_trades_table
        )
        # Capture outcomes
        #todo: Calculate trade outcomes function
        #todo: Save trade outcomes to SQL (preparation for optimization)

    # Construct the trades
    if optimize:
        # Optimize the take profit.

        pass

    if display:
        trade_object = {
            "trade_table_name": trade_table_name,
            "strategy": strategy_name,
            "comment": comment
        }
        # Retrieve raw dataframe
        raw_dataframe = sql_interaction.retrieve_dataframe(
            table_name=raw_data_table_name,
            project_settings=project_settings
        )
        # Retrieve an image of events
        strategy_image = ema_cross.ema_cross_strategy(
            dataframe=raw_dataframe,
            risk_ratio=variables['risk_ratio'],
            display=True,
            backtest=False
        )
        # Retrieve trades dataframe
        trades_dataframe = ema_cross.ema_cross_strategy(
            dataframe=raw_dataframe,
            risk_ratio=variables["risk_ratio"],
            backtest=True
        )
        # Retrieve trade object
        trades_outcome = calculate_trades(
            trade_object=trade_object,
            comment=comment,
            project_settings=project_settings
        )
        print(trades_outcome)
        # Add trades outcomes to graph
        # todo: retrieve calculated trades
        # todo: retrieve balance
        # todo: pass to display function
        show_display(
            strategy_image=strategy_image,
            trades_outcome=trades_outcome,
            proposed_trades=trades_dataframe,
            strategy=strategy_name,
            symbol=symbol
        )

    return True


# Function to display backtest details to user
def show_display(strategy_image, trades_outcome, proposed_trades, symbol, strategy):
    # Construct the Title
    title = symbol + " " + strategy
    # Add trades to strategy image
    strategy_with_trades = display_lib.add_trades_to_graph(
        trades_dict=trades_outcome,
        base_fig=strategy_image
    )
    # Turn proposed trades into a subplot
    prop_trades_figure = display_lib.add_dataframe(proposed_trades)


    display_lib.display_backtest(
        original_strategy=strategy_image,
        strategy_with_trades=strategy_with_trades,
        table=prop_trades_figure,
        graph_title=title
    )


# Function to retrieve and construct trade open and sell
def calculate_trades(trade_object, comment, project_settings):
    # Retrieve the trades for the strategy being analyzed
    trades = sql_interaction.retrieve_unique_order_id(
        trade_object=trade_object,
        comment=comment,
        project_settings=project_settings)
    trade_list = []
    full_trades = []
    # Format the trades into a nicer list
    for trade in trades:
        trade_list.append(trade[0])

    # Setup trackers for wins and losses
    summary = {
        "wins": 0,
        "losses": 0,
        "profit": 0,
        "not_completed": 0
    }

    # Retrieve full details for each trade
    for order in trade_list:
        trade_view = {'name': order}

        trade_details = sql_interaction.retrieve_trade_details(
            order_id=order,
            trade_object=trade_object,
            comment=comment,
            project_settings=project_settings
        )
        trade_view['trade_type'] = trade_details[0][3]
        # Calculate the outcome
        for entry in trade_details:
            if entry[12] == "expired":
                trade['expired'] = True
                trade['expire_price'] = entry[10]
                trade['expire_time'] = datetime.datetime.fromtimestamp(entry[16], pytz.UTC)
            elif entry[12] == "opened":
                trade_view['open_price'] = entry[10]
                trade_view['open_time'] = datetime.datetime.fromtimestamp(entry[16], pytz.UTC)
            elif entry[12] == "closed":
                trade_view['close_price'] = entry[10]
                trade_view['close_time'] = datetime.datetime.fromtimestamp(entry[16], pytz.UTC)
                trade_view['trade_outcome'] = calc_the_win(row=entry)
            elif entry[12] == "order":
                trade_view['order_price'] = entry[10]
                trade_view['order_time'] = datetime.datetime.fromtimestamp(entry[16], pytz.UTC)
            elif entry[12] == "backtest_closed":
                trade_view['close_price'] = entry[10]
                trade_view['close_time'] = datetime.datetime.fromtimestamp(entry[16], pytz.UTC)
                trade_view['trade_outcome'] = {"not_completed": True}
        full_trades.append(trade_view)

    # Calculate the wins and losses
    for trade_outcome in full_trades:
        if not trade_outcome["trade_outcome"]["not_completed"]:
            summary['profit'] += trade_outcome['trade_outcome']['profit']
            if trade_outcome['trade_outcome']['win'] is True:
                summary['wins'] += 1
            else:
                summary['losses'] += 1
        else:
            summary['not_completed'] += 1
    summary["full_trades"] = full_trades
    return summary


# Function to calculate if a trade was a win or loss and profit
def calc_the_win(row):
    # Set up record
    outcome = {
        "profit": 0,
        "win": False,
        "not_completed": False
    }
    # Branch based on order type
    if row[3] == "BUY_STOP":
        # Calculate the profit
        outcome["profit"] = (row[18] - row[17]) * row[6]
    else:
        # Calculate the profit
        outcome["profit"] = (row[17] - row[18]) * row[6]
    # Profit will be any number > 0
    if outcome["profit"] > 0:
        outcome['win'] = True
    else:
        outcome['win'] = False
    # Return outcome
    return outcome



