from sql_lib import sql_interaction
import display_lib
import datetime
import pandas
from backtest_lib import setup_backtest, backtest
from strategies import ema_cross


# Function to initiate and manage backtest
def do_backtest(strategy_name, symbol, candle_timeframe, test_timeframe, project_settings, get_data=True,
                exchange="mt5", optimize=False, show_only=False, optimize_variables={}):
    risk_ratio = 3
    symbol_name = symbol.split(".")
    # Set the table names
    table_name_base = strategy_name + "_" + symbol_name[0] + "_"
    raw_data_table_name = f"{table_name_base}candles".lower()
    tick_data_table_name = f"{table_name_base}ticks".lower()
    trade_table_name = f"{table_name_base}trade_actions".lower()
    balance_tracker_table = f"{table_name_base}balance".lower()
    valid_trades_table = f"{table_name_base}trades".lower()
    if get_data:
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

    raw_dataframe = sql_interaction.retrieve_dataframe(
        table_name=raw_data_table_name,
        project_settings=project_settings
    )
    # Construct the trades
    if optimize:
        # Optimize the take profit.

        pass
    elif show_only:
        trade_object = {
            "trade_table_name": trade_table_name,
            "strategy": strategy_name,
        }
        # Get the base figure
        trades_dataframe = ema_cross.ema_cross_strategy(
            dataframe=raw_dataframe,
            risk_ratio=risk_ratio,
            backtest=False
        )
        show_user(
            trade_object=trade_object,
            base_fig=trades_dataframe[0],
            project_settings=project_settings,
            strategy=strategy_name,
            symbol=symbol
        )
    else:
        # Construct the trades
        trades_dataframe = ema_cross.ema_cross_strategy(
            dataframe=raw_dataframe,
            risk_ratio=3
        )
        # Run the backtester
        backtest.backtest(
            valid_trades_dataframe=trades_dataframe[0],
            time_orders_valid=1800,
            tick_data_table_name=tick_data_table_name,
            trade_table_name=trade_table_name,
            project_settings=project_settings,
            strategy=strategy_name,
            symbol=symbol,
            comment="initial_test",
            balance_table=balance_tracker_table,
            valid_trades_table=valid_trades_table
        )
        # Construct trade object
        trade_object = {
            "trade_table_name": trade_table_name,
            "strategy": strategy_name,
        }
        show_user(
            trade_object=trade_object,
            base_fig=trades_dataframe[1],
            project_settings=project_settings,
            strategy=strategy_name,
            symbol=symbol
        )


# Function to display backtest details to user
def show_user(trade_object, base_fig, project_settings, symbol, strategy):
    # Construct the Title
    title = symbol + " " + strategy
    # Retrieve a list of the trades
    trades = retrieve_trades(trade_object, project_settings)
    # Get the figure for trades
    trades_fig = display_lib.add_trades_to_graph(trades, display_on_base=False)
    # Update the title
    trades_title = title + " Trades"
    # Update the base fig
    # base_fig = base_fig.add_trace(trades_fig)
    display_lib.display_graph(base_fig, title, dash=True)
    # Send to backtest display
    #display_lib.backtest_display(base_fig, trades_fig, base_fig, title)


# Function to retrieve and construct trade open and sell
def retrieve_trades(trade_object, project_settings):
    trades = sql_interaction.retrieve_unique_order_id(trade_object, project_settings)
    trade_list = []
    full_trades = []
    # Format the trades into a nicer list
    for trade in trades:
        trade_list.append(trade[0])

    # Retrieve full details for each trade
    for order in trade_list:
        trade_view = {}
        trade_view['name'] = order

        trade_details = sql_interaction.retrieve_trade_details(order_id=order, trade_object=trade_object,
                                                               project_settings=project_settings)
        trade_view['trade_type'] = trade_details[0][3]
        for entry in trade_details:
            if entry[12] == "opened":
                trade_view['open_price'] = entry[10]
                trade_view['open_time'] = datetime.datetime.fromtimestamp(entry[16])
            elif entry[12] == "closed":
                trade_view['close_price'] = entry[10]
                trade_view['close_time'] = datetime.datetime.fromtimestamp(entry[16])
        full_trades.append(trade_view)
    return full_trades
