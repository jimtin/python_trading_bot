import talib
import display_lib


def rsi(dataframe, period=14, display=False, fig=None):
    """
    Function to calculate the RSI indicator. More details can be found here: https://appnologyjames.medium.com/how-to-add-the-rsi-indicator-to-your-algorithmic-python-trading-bot-bf5795756365
    :param dataframe: dataframe object where the RSI should be calculated on
    :param period: period for the RSI calculation
    :param display: boolean to determine whether the RSI should be displayed on the graph
    :param fig: plotly figure object to add the RSI to
    :return: dataframe with RSI column added
    """
    df = dataframe.copy()
    # Calculate RSI col on dataframe
    df['rsi'] = 0
    df['rsi'] = talib.RSI(df['close'], timeperiod=period)

    if display:  # add the RSI to the graph
        # todo: Figure out how to make a subplot with RSI
        fig = display_lib.add_line_to_graph(
            base_fig=fig,
            dataframe=df,
            dataframe_column='rsi',
            line_name='RSI'
        )

    return df
