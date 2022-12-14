import psycopg2
import psycopg2.extras


# Function to connect to PostgreSQL database
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
        print(sql_query)
        # Create the cursor
        cursor = conn.cursor()
        # Execute the cursor query
        cursor.execute(sql_query)
        # Commit the changes
        conn.commit()
        return True
    except (Exception, psycopg2.Error) as e:
        print(f"Failed to execute query: {e}")
        return Exception
    finally:
        # If conn has completed, close
        if conn is not None:
            conn.close()


# Function to create a table
def create_sql_table(table_name, table_details, project_settings):
    """
    Function to create a table in SQL
    :param table_name: String
    :param table_details: String
    :param project_settings: JSON Object
    :return: Boolean
    """
    # Create the query string
    sql_query = f"CREATE TABLE {table_name} (id SERIAL PRIMARY KEY, {table_details})"
    # Execute the query
    return sql_execute(sql_query=sql_query, project_settings=project_settings)


# Function to create a trade table
def create_trade_table(table_name, project_settings):
    """
    Function to create a trade table in SQL
    :param table_name: string
    :param project_settings: JSON Object
    :return: Boolean
    """
    # Define the table according to the CIM: https://github.com/jimtin/python_trading_bot/blob/master/common_information_model.json
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
                    f"status VARCHAR(100) NOT NULL"
    # Pass to Create Table function
    return create_sql_table(table_name=table_name, table_details=table_details, project_settings=project_settings)


# Function to insert a trade action into SQL database
def insert_trade_action(table_name, trade_information, project_settings):
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
                    f"take_profit, price, comment, status) VALUES (" \
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
                    f"'{ti['status']}'" \
                    f")"
        # Execute the query
        return sql_execute(sql_query=sql_query, project_settings=project_settings)
    else:
        # Return an exception
        return Exception # Custom Error Handling Coming Soon

