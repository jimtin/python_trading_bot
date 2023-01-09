import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine
import pandas

# Function to connect to PostgreSQL database
import exceptions


def postgres_connect(project_settings):
    """
    Function to connect to PostgreSQL database
    :param project_settings: json object
    :return: connection object
    """
    # Define the connection
    try:
        conn = psycopg2.connect(
            database=project_settings['postgres']['database'],
            user=project_settings['postgres']['user'],
            password=project_settings['postgres']['password'],
            host=project_settings['postgres']['host'],
            port=project_settings['postgres']['port']
        )
        return conn
    except Exception as e:
        print(f"Error connecting to Postgres: {e}")
        return False


# Function to execute SQL
def sql_execute(sql_query, project_settings):
    """
    Function to execute SQL statements
    :param sql_query: String
    :return: Boolean
    """
    # Create a connection
    conn = postgres_connect(project_settings=project_settings)
    # Execute the query
    try:
        # print(sql_query)
        # Create the cursor
        cursor = conn.cursor()
        # Execute the cursor query
        cursor.execute(sql_query)
        # Commit the changes
        conn.commit()
        return True
    except (Exception, psycopg2.Error) as e:
        print(f"Failed to execute query: {e}")
        raise e
    finally:
        # If conn has completed, close
        if conn is not None:
            conn.close()


# Function to create a table
def create_sql_table(table_name, table_details, project_settings, id=True):
    """
    Function to create a table in SQL
    :param table_name: String
    :param table_details: String
    :param project_settings: JSON Object
    :return: Boolean
    """
    # Create the query string
    if id:
        # Create an auto incrementing primary key
        sql_query = f"CREATE TABLE {table_name} (id SERIAL PRIMARY KEY, {table_details})"
    else:
        # Create without an auto incrementing primary key
        sql_query = f"CREATE TABLE {table_name} (id BIGINT NOT NULL, {table_details})"
    # Execute the query
    create_table = sql_execute(sql_query=sql_query, project_settings=project_settings)
    if create_table:
        return True
    raise exceptions.SQLTableCreationError


# Function to retrieve data from SQL
def get_data(sql_query, project_settings):
    conn = postgres_connect(project_settings)
    cur = conn.cursor()
    cur.execute(sql_query)
    result = cur.fetchall()
    return result


# Function to create a trade table
def create_trade_table(table_name, project_settings):
    """
    Function to create a trade table in SQL
    :param table_name: string
    :param project_settings: JSON Object
    :return: Boolean
    """
    # Define the table according to the CIM:
    # https://github.com/jimtin/python_trading_bot/blob/master/common_information_model.json
    table_details = f"strategy VARCHAR(100) NOT NULL," \
                    f"exchange VARCHAR(100) NOT NULL," \
                    f"trade_type VARCHAR(50) NOT NULL," \
                    f"trade_stage VARCHAR(50) NOT NULL," \
                    f"symbol VARCHAR(50) NOT NULL," \
                    f"volume FLOAT4 NOT NULL," \
                    f"stop_loss FLOAT4 NOT NULL," \
                    f"take_profit FLOAT4 NOT NULL," \
                    f"price FLOAT4 NOT NULL," \
                    f"comment VARCHAR(250) NOT NULL," \
                    f"status VARCHAR(100) NOT NULL," \
                    f"order_id VARCHAR(100) NOT NULL"
    # Pass to Create Table function
    return create_sql_table(table_name=table_name, table_details=table_details, project_settings=project_settings)


# Function to insert a trade action into SQL database
def insert_trade_action(table_name, trade_information, project_settings, backtest=False):
    """
    Function to insert a row of trade data
    :param table_name: String
    :param trade_information: Dictionary
    :return: Bool
    """
    # Make sure that only valid tables entered
    if table_name == "paper_trade_table" or table_name == "live_trade_table":
        # Make trade_information shorter
        ti = trade_information
        # Construct the SQL Query
        sql_query = f"INSERT INTO {table_name} (strategy, exchange, trade_type, trade_stage, symbol, volume, stop_loss, " \
                    f"take_profit, price, comment, status, order_id) VALUES (" \
                    f"'{ti['strategy']}'," \
                    f"'{ti['exchange']}'," \
                    f"'{ti['trade_type']}'," \
                    f"'{ti['trade_stage']}'," \
                    f"'{ti['symbol']}'," \
                    f"{ti['volume']}," \
                    f"{ti['stop_loss']}," \
                    f"{ti['take_profit']}," \
                    f"{ti['price']}," \
                    f"'{ti['comment']}'," \
                    f"'{ti['status']}'," \
                    f"'{ti['order_id']}'" \
                    f")"
        # Execute the query
        return sql_execute(sql_query=sql_query, project_settings=project_settings)
    elif backtest:
        sql_query = f"INSERT INTO {table_name} "
    else:
        # Return an exception
        return Exception  # Custom Error Handling Coming Soon


# Function to insert a live trade action into SQL database
def insert_live_trade_action(trade_information, project_settings):
    """
    Function to insert a row of trade data into the table live_trade_table
    :param trade_information: Dictionary object of trade
    :param project_settings: Dictionary object of project details
    :return: Bool
    """
    return insert_trade_action(
        table_name="live_trade_table",
        trade_information=trade_information,
        project_settings=project_settings
    )


# Function to insert a paper trade action into SQL database
def insert_paper_trade_action(trade_information, project_settings):
    """
    Function to insert a row of trade data into the table paper_trade_table
    :param trade_information: Dictionary object of trade details
    :param project_settings: Dictionary object of project details
    :return: Bool
    """
    return insert_trade_action(
        table_name="paper_trade_table",
        trade_information=trade_information,
        project_settings=project_settings
    )


# Function to create a backtest tick table
def create_mt5_backtest_tick_table(table_name, project_settings):
    # Define the columns in the table
    table_details = f"symbol VARCHAR(100) NOT NULL," \
                    f"time BIGINT NOT NULL," \
                    f"bid FLOAT4 NOT NULL," \
                    f"ask FLOAT4 NOT NULL," \
                    f"spread FLOAT4 NOT NULL," \
                    f"last FLOAT4 NOT NULL," \
                    f"volume FLOAT4 NOT NULL," \
                    f"flags BIGINT NOT NULL," \
                    f"volume_real FLOAT4 NOT NULL," \
                    f"time_msc BIGINT NOT NULL," \
                    f"human_time DATE NOT NULL," \
                    f"human_time_msc DATE NOT NULL"
    # Create the table
    return create_sql_table(table_name=table_name, table_details=table_details, project_settings=project_settings,
                            id=False)


# Function to create a candlestick backtest table
def create_mt5_backtest_raw_candlestick_table(table_name, project_settings):
    # Define the columns in the table
    table_details = f"symbol VARCHAR(100) NOT NULL," \
                    f"time BIGINT NOT NULL," \
                    f"timeframe VARCHAR(100) NOT NULL," \
                    f"open FLOAT4 NOT NULL," \
                    f"high FLOAT4 NOT NULL," \
                    f"low FLOAT4 NOT NULL," \
                    f"close FLOAT4 NOT NULL," \
                    f"tick_volume FLOAT4 NOT NULL," \
                    f"spread FLOAT4 NOT NULL," \
                    f"real_volume FLOAT4 NOT NULL," \
                    f"human_time DATE NOT NULL," \
                    f"human_time_msc DATE NOT NULL"
    # Create the table
    return create_sql_table(table_name=table_name, table_details=table_details, project_settings=project_settings)


# Function to create a trade backtest table
def create_mt5_backtest_trade_table(table_name, project_settings):
    # Define the table according to the CIM:
    # https://github.com/jimtin/python_trading_bot/blob/master/common_information_model.json
    table_details = f"strategy VARCHAR(100) NOT NULL," \
                    f"exchange VARCHAR(100) NOT NULL," \
                    f"trade_type VARCHAR(50) NOT NULL," \
                    f"trade_stage VARCHAR(50) NOT NULL," \
                    f"symbol VARCHAR(50) NOT NULL," \
                    f"qty_purchased FLOAT4 NOT NULL," \
                    f"leverage FLOAT4 NOT NULL," \
                    f"stop_loss FLOAT4 NOT NULL," \
                    f"take_profit FLOAT4 NOT NULL," \
                    f"price FLOAT4 NOT NULL," \
                    f"comment VARCHAR(250) NOT NULL," \
                    f"status VARCHAR(100) NOT NULL," \
                    f"order_id VARCHAR(100) NOT NULL," \
                    f"balance FLOAT4 NOT NULL," \
                    f"equity FLOAT4 NOT NULL," \
                    f"update_time FLOAT4 NOT NULL," \
                    f"entry_price FLOAT4 NOT NULL," \
                    f"exit_price FLOAT4 NOT NULL"
    return create_sql_table(table_name=table_name, table_details=table_details, project_settings=project_settings,
                            id=True)


# Function to write to SQL from csv file
def upload_from_csv(csv_location, table_name, project_settings):
    conn = postgres_connect(project_settings)
    cur = conn.cursor()
    with open(csv_location, 'r') as f:
        cur.copy_from(f, table_name, ',')

    f.close()

    conn.commit()
    conn.close()


# Function to retrieve dataframe from Postgres table
def retrieve_dataframe(table_name, project_settings, chunky=False, tick_data=False):
    # Create the connection object for PostgreSQL
    engine_string = f"postgresql://{project_settings['postgres']['user']}:{project_settings['postgres']['password']}@" \
                    f"{project_settings['postgres']['host']}:{project_settings['postgres']['port']}/" \
                    f"{project_settings['postgres']['database']}"
    engine = create_engine(engine_string)
    # Create the query
    if tick_data:
        sql_query = f"SELECT * FROM {table_name} ORDER BY time_msc;"
    else:
        sql_query = f"SELECT * FROM {table_name} ORDER BY time;"
    if chunky:
        # Set the chunk size
        chunk_size = 10000  # You may need to adjust this based upon your processor
        # Set up database chunking
        db_connection = engine.connect().execution_options(
            max_row_buffer=chunk_size
        )
        # Retrieve the data
        dataframe = pandas.read_sql(sql_query, db_connection, chunksize=chunk_size)
        # Close the connection
        db_connection.close()
        # Return the dataframe
        return dataframe
    else:
        # Standard DB connection
        db_connection = engine.connect()
        # Retrieve the data
        dataframe = pandas.read_sql(sql_query, db_connection)
        # Close the connection
        db_connection.close()
        # Return the dataframe
        return dataframe


# Function to add a backtest update
def insert_backtest_update(strategy, exchange, trade_type, trade_stage, symbol, qty_purchased, leverage, stop_loss,
                           take_profit, price, comment, status, order_id, available_balance, equity, table_name,
                           project_settings, update_time, entry_price, exit_price):
    # Create the SQL statement
    sql_query = f"INSERT INTO {table_name} (strategy, exchange, trade_type, trade_stage, symbol, qty_purchased, " \
                f"leverage, stop_loss, take_profit, price, comment, status, order_id, balance, equity, update_time, " \
                f"entry_price, exit_price) VALUES (" \
                f"'{strategy}'," \
                f"'{exchange}'," \
                f"'{trade_type}'," \
                f"'{trade_stage}'," \
                f"'{symbol}'," \
                f"'{qty_purchased}'," \
                f"'{leverage}'," \
                f"'{stop_loss}'," \
                f"'{take_profit}'," \
                f"'{price}'," \
                f"'{comment}'," \
                f"'{status}'," \
                f"'{order_id}'," \
                f"'{available_balance}'," \
                f"'{equity}'," \
                f"'{update_time}'," \
                f"'{entry_price}'," \
                f"'{exit_price}'" \
                f");"
    try:
        return sql_execute(sql_query=sql_query, project_settings=project_settings)
    except Exception as e:
        raise exceptions.SQLBacktestTradeActionError


# Function to add a new order from backtester
def insert_order_update(trade_type, status, stop_loss, take_profit, price, order_id, trade_object, update_time,
                        project_settings):
    return insert_backtest_update(
        strategy=trade_object["strategy"],
        exchange="testing",
        trade_type=trade_type,
        trade_stage="order",
        symbol=trade_object["symbol"],
        qty_purchased=0.00,
        leverage=trade_object["backtest_settings"]["leverage"],
        stop_loss=stop_loss,
        take_profit=take_profit,
        price=price,
        comment="backtest",
        status=status,
        order_id=order_id,
        available_balance=trade_object["current_available_balance"],
        equity=trade_object["current_equity"],
        update_time=update_time,
        table_name=trade_object["trade_table_name"],
        project_settings=project_settings,
        entry_price=0.00,
        exit_price=0.00
    )


def insert_new_position(trade_type, status, stop_loss, take_profit, price, order_id, trade_object, update_time,
                        project_settings, qty_purchased, entry_price):
    return insert_backtest_update(
        strategy=trade_object["strategy"],
        exchange="testing",
        trade_type=trade_type,
        trade_stage="position",
        symbol=trade_object["symbol"],
        qty_purchased=qty_purchased,
        leverage=trade_object["backtest_settings"]['leverage'],
        stop_loss=stop_loss,
        take_profit=take_profit,
        price=price,
        comment="backtest",
        status=status,
        order_id=order_id,
        available_balance=trade_object["current_available_balance"],
        equity=trade_object["current_equity"],
        table_name=trade_object["trade_table_name"],
        update_time=update_time,
        project_settings=project_settings,
        entry_price=entry_price,
        exit_price=0.00
    )


def position_close(trade_type, status, stop_loss, take_profit, price, order_id, trade_object, update_time,
                           project_settings, qty_purchased, trade_stage, entry_price, exit_price):
    return insert_backtest_update(
        strategy=trade_object["strategy"],
        exchange="testing",
        trade_type=trade_type,
        trade_stage=trade_stage,
        symbol=trade_object["symbol"],
        qty_purchased=qty_purchased,
        leverage=trade_object["backtest_settings"]['leverage'],
        stop_loss=stop_loss,
        take_profit=take_profit,
        price=price,
        comment="backtest",
        status=status,
        order_id=order_id,
        available_balance=trade_object["current_available_balance"],
        equity=trade_object["current_equity"],
        table_name=trade_object["trade_table_name"],
        update_time=update_time,
        project_settings=project_settings,
        entry_price=entry_price,
        exit_price=exit_price
    )


# Retrieve last take_profit entry for an order
def retrieve_last_position(order_id, trade_object, project_settings):
    # Create the SQL query
    sql_query = f"SELECT * FROM {trade_object['trade_table_name']} WHERE symbol='{trade_object['symbol']}' AND " \
                f"strategy='{trade_object['strategy']}' AND order_id='{order_id}' ORDER BY id DESC LIMIT 1;"
    # Execute the SQL Query
    return get_data(sql_query, project_settings)


# Function to save a dataframe
def save_dataframe(dataframe, table_name, project_settings):
    # Create the connection object for PostgreSQL
    engine_string = f"postgresql://{project_settings['postgres']['user']}:{project_settings['postgres']['password']}@" \
                    f"{project_settings['postgres']['host']}:{project_settings['postgres']['port']}/" \
                    f"{project_settings['postgres']['database']}"
    engine = create_engine(engine_string)
    # Save
    dataframe.to_sql(table_name, engine, if_exists='append')

