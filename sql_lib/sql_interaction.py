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
