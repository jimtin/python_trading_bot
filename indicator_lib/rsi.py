import talib
import display_lib


# Function to calculate the RSI indicator
def rsi(dataframe, period=14, display=False, fig=None):
    """
    Function to calculate the RSI indicator. More details can be found here: https://appnologyjames.medium.com/how-to-add-the-rsi-indicator-to-your-algorithmic-python-trading-bot-bf5795756365
    :param dataframe: dataframe object where the RSI should be calculated on
    :param period: period for the RSI calculation
    :param display: boolean to determine whether the RSI should be displayed on the graph
    :param fig: plotly figure object to add the RSI to
    :return: dataframe with RSI column added
    """
    # Copy the dataframe
    dataframe = dataframe.copy()
    # Add RSI column to dataframe
    dataframe['rsi'] = 0
    # Calculate RSI on dataframe
    dataframe['rsi'] = talib.RSI(dataframe['close'], timeperiod=period)
    # If display is true, add the RSI to the graph
    if display:
        # todo: Figure out how to make a subplot with RSI
        # Add RSI to graph
        fig = display_lib.add_line_to_graph(
            base_fig=fig,
            dataframe=dataframe,
            dataframe_column='rsi',
            line_name='RSI'
        )
    return dataframe
