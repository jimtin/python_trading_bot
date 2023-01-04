from sql_lib import sql_interaction
import pandas
import plotly.graph_objects as go
from indicators import ta_sma


# Function to retrieve back_test data and then display chart of close values
def show_data(project_settings):
    # Table Name
    table_name = "test_script_mt5_backtest_raw_candles"
    # Get the data
    dataframe = sql_interaction.retrieve_dataframe(table_name, project_settings)
    # Construct the figure
    fig = go.Figure(data=[go.Candlestick(
        x=dataframe['human_time'],
        open=dataframe['open'],
        high=dataframe['high'],
        close=dataframe['close'],
        low=dataframe['low']
    )])

    fig.add_trace(go.Scatter(
                x=dataframe['human_time'],
                y=dataframe['ta_sma_200']
            )
    )

    fig.add_trace(go.Scatter(
        x=dataframe['human_time'],
        y=dataframe['ta_ema_200']
    ))
    # Display the figure
    fig.show()


