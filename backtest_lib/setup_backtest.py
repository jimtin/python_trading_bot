import stat

import numpy
import pandas
import psycopg2

import exceptions
from sql_lib import sql_interaction
from metatrader_lib import mt5_interaction
import datetime
from sqlalchemy import create_engine
from dateutil.relativedelta import relativedelta
import os
from indicators import calc_all_indicators


"""
Pseudo Code:
1. Create tables -> tick, candlestick, trade, exchange
2. Get raw data
3. Add values
4. Save completed data
"""


# Function to set up the backtester
def set_up_backtester(strategy_name, symbol, candle_timeframe, backtest_timeframe, project_settings, exchange,
                      candle_table_name, tick_table_name, balance_tracker_table):
    # Create the backtest tables
    create_backtest_tables(tick_table_name=tick_table_name,
                           balance_tracker_table=balance_tracker_table,
                           project_settings=project_settings)
    # Get the datetime now
    current_datetime = datetime.datetime.now()
    current_datetime = current_datetime.astimezone(datetime.timezone.utc)
    # Populate the raw data based upon easily selected timeframes
    if backtest_timeframe == "month":
        previous_datetime = current_datetime - relativedelta(months=1)
        pass
    elif backtest_timeframe == "5days":
        previous_datetime = current_datetime - relativedelta(days=5)
        pass
    elif backtest_timeframe == "6month":
        previous_datetime = current_datetime - relativedelta(months=6)
        pass
    elif backtest_timeframe == "year":
        previous_datetime = current_datetime - relativedelta(years=1)
        pass
    elif backtest_timeframe == "2years":
        previous_datetime = current_datetime - relativedelta(years=2)
        pass
    elif backtest_timeframe == "5years":
        previous_datetime = current_datetime - relativedelta(years=5)
        pass
    else:
        print("Choose correct value for backtester")
        raise exceptions.BacktestIncorrectBacktestTimeframeError

    if exchange == "mt5":
        # Retrieve data
        retrieve_mt5_backtest_data(
            symbol=symbol,
            strategy=strategy_name,
            candlesticks=candle_timeframe,
            start_time_utc=previous_datetime,
            finish_time_utc=current_datetime,
            project_settings=project_settings,
            tick_table_name=tick_table_name,
            candlestick_table_name=candle_table_name
        )


# Create the backtest tables
def create_backtest_tables(tick_table_name, balance_tracker_table, project_settings):
    # Create the tick data table
    try:
        sql_interaction.create_mt5_backtest_tick_table(table_name=tick_table_name, project_settings=project_settings)
        sql_interaction.create_balance_tracker_table(table_name=balance_tracker_table, project_settings=project_settings)
    except Exception as e:
        print(f"Error creating backtest tables. {e}")
    return True


# Retrieve data
def retrieve_mt5_backtest_data(symbol, strategy, project_settings, candlesticks, start_time_utc, finish_time_utc,
                               tick_table_name, candlestick_table_name):
    # Create the connection object for PostgreSQL
    engine_string = f"postgresql://{project_settings['postgres']['user']}:{project_settings['postgres']['password']}@" \
                    f"{project_settings['postgres']['host']}:{project_settings['postgres']['port']}/" \
                    f"{project_settings['postgres']['database']}"
    engine = create_engine(engine_string)
    # Initialize MT5. Use this to prepare for multiprocessing
    print("Starting MT5")
    mt5_interaction.start_mt5(
        username=project_settings["mt5"]["paper"]["username"],
        password=project_settings["mt5"]["paper"]["password"],
        server=project_settings["mt5"]["paper"]["server"],
        path=project_settings["mt5"]["paper"]["mt5Pathway"],
    )
    # Enable Symbol
    print(f"Initializing symbol {symbol}")
    mt5_interaction.initialize_symbols([symbol])
    # Retrieve tick data
    print(f"Retrieving tick data for {symbol} from MT5")
    ticks_data_frame = retrieve_mt5_tick_data(
        start_time=start_time_utc,
        finish_time=finish_time_utc,
        symbol=symbol
    )
    # Reorder to match creation
    ticks_data_frame = ticks_data_frame[['symbol', 'time', 'bid', 'ask', 'spread', 'last', 'volume', 'flags',
                                         'volume_real', 'time_msc', 'human_time', 'human_time_msc']]
    # Write to database
    print(f"Writing tick data for {symbol} to local database")
    upload_to_postgres(ticks_data_frame, tick_table_name, project_settings)
    # Retrieve candlestick data
    for candle in candlesticks:
        print(f"Retrieving {candle} data for {symbol}")
        candlestick_data = retrieve_mt5_candle_data(
            start_time=start_time_utc,
            finish_time=finish_time_utc,
            timeframe=candle,
            symbol=symbol
        )
        # Calculate all indicators
        candlestick_data = calc_all_indicators.all_indicators(candlestick_data)
        # Write to database
        candlestick_data.to_sql(name=candlestick_table_name, con=engine, if_exists='append')
    return True


# Helper function to divide a given date range by 2
def split_time_range_in_half(start_time, finish_time):
    n = 2
    split_timeframe = []
    diff = (finish_time - start_time) // n
    for idx in range(0, n):
        split_timeframe.append((start_time + idx * diff))
    split_timeframe.append(finish_time)
    return split_timeframe


# Function to retrieve MT5 Tick data with autoscaling options
def retrieve_mt5_tick_data(start_time, finish_time, symbol):
    # Attempt to retrieve tick data
    tick_data = mt5_interaction.retrieve_tick_time_range(
        start_time_utc=start_time,
        finish_time_utc=finish_time,
        symbol=symbol
    )
    # Autoscale if Zero results retrieved
    if type(tick_data) is not numpy.ndarray:
        print(f"Auto scaling tick query for {symbol}")
        # Split timerange into 2
        split_timeframe = split_time_range_in_half(start_time=start_time, finish_time=finish_time)
        # Iterate through timeframe list and append
        start_time = split_timeframe[0]
        tick_data_autoscale = pandas.DataFrame()
        for timeframe in split_timeframe:
            if timeframe == split_timeframe[0]:
                # Initial pass, so ignore
                pass

            else:
                tick_data_new = retrieve_mt5_tick_data(start_time=start_time, finish_time=timeframe, symbol=symbol)
                tick_data_autoscale = pandas.concat([tick_data_autoscale, tick_data_new])
                start_time = timeframe
        return tick_data_autoscale
    # Else return value
    ticks_data_frame = pandas.DataFrame(tick_data)

    # Add spread
    ticks_data_frame['spread'] = ticks_data_frame['ask'] - ticks_data_frame['bid']
    # Add symbol
    ticks_data_frame['symbol'] = symbol
    # Format integers into signed integers (postgres doesn't support unsigned int)
    ticks_data_frame['time'] = ticks_data_frame['time'].astype('int64')
    ticks_data_frame['volume'] = ticks_data_frame['volume'].astype('int64')
    ticks_data_frame['time_msc'] = ticks_data_frame['time_msc'].astype('int64')
    ticks_data_frame['human_time'] = pandas.to_datetime(ticks_data_frame['time'], unit='s')
    ticks_data_frame['human_time_msc'] = pandas.to_datetime(ticks_data_frame['time_msc'], unit='ms')
    return ticks_data_frame


# Function to retrieve mt5 candlestick data
def retrieve_mt5_candle_data(start_time, finish_time, timeframe, symbol):
    # Retrieve the candlestick data
    candlestick_data = mt5_interaction.retrieve_candlestick_data_range(
        start_time_utc=start_time,
        finish_time_utc=finish_time,
        timeframe=timeframe,
        symbol=symbol
    )
    if type(candlestick_data) is not numpy.ndarray:
        print(f"Auto scaling candlestick query for {symbol} and {timeframe}")
        # Split time range in 2
        split_timeframe = split_time_range_in_half(start_time=start_time, finish_time=finish_time)
        # Iterate through the timeframe list and construct full list
        start_time = split_timeframe[0]
        candlestick_data_autoscale = pandas.DataFrame()
        for time in split_timeframe:
            if time == split_timeframe[0]:
                # Initial pass, so ignore
                pass
            else:
                candlestick_data_new = retrieve_mt5_candle_data(
                    start_time=start_time,
                    finish_time=time,
                    timeframe=timeframe,
                    symbol=symbol
                )
                candlestick_data_autoscale = pandas.concat([candlestick_data_autoscale, candlestick_data_new])
        return candlestick_data_autoscale

    # Convert to a dataframe
    candlestick_dataframe = pandas.DataFrame(candlestick_data)
    # Add in symbol and timeframe columns
    candlestick_dataframe['symbol'] = symbol
    candlestick_dataframe['timeframe'] = timeframe
    # Convert integers into signed integers (postgres doesn't support unsigned int)
    candlestick_dataframe['time'] = candlestick_dataframe['time'].astype('int64')
    candlestick_dataframe['tick_volume'] = candlestick_dataframe['tick_volume'].astype('float64')
    candlestick_dataframe['spread'] = candlestick_dataframe['spread'].astype('int64')
    candlestick_dataframe['real_volume'] = candlestick_dataframe['real_volume'].astype('int64')
    candlestick_dataframe['human_time'] = pandas.to_datetime(candlestick_dataframe['time'], unit='s')
    return candlestick_dataframe


# Function to upload a dataframe to Postgres
def upload_to_postgres(dataframe, table_name, project_settings):
    ## Process to upload to local database: Get directory, write to csv, update CSV permissions, upload to DB,
    # delete CSV

    # Specify the disk location
    current_user = os.getlogin()
    dataframe_csv = f"C:\\Users\\{current_user}\\Desktop\\ticks_data_frame.csv"

    # Dump the dataframe to disk
    dataframe.to_csv(dataframe_csv, index_label='id', header=False)

    # Open the csv
    f = open(dataframe_csv, 'r')

    # Connect to database
    conn = sql_interaction.postgres_connect(project_settings)
    cursor = conn.cursor()

    # Try to upload
    try:
        cursor.copy_from(f, table_name, sep=",")
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        f.close()
        os.remove(dataframe_csv)
        print(f"Postgres upload error: {error}")
        conn.rollback()
        cursor.close()
        return 1
    print(f"Postgres upload completed")
    cursor.close()
    f.close()
    os.remove(dataframe_csv)
    return True
