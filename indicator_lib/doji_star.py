import talib
import display_lib

def doji_star(dataframe, display=False, fig=None):
    """
    Function to calculate the doji star indicator. This is a candlestick pattern, more details can be found here:
    https://medium.com/me/stats/post/28c12f04caf6
    :param data: dataframe object where the Doji Star patterns should be detected on
    :param display: boolean to determine whether the Doji Star patterns should be displayed on the graph
    :param fig: plotly figure object to add the Doji Star patterns to
    :return: dataframe with Doji Star patterns identified
    """
    # Copy the dataframe
    dataframe = dataframe.copy()
    # Add doji star column to dataframe
    dataframe['doji_star'] = 0
    # Calculate doji star on dataframe

    dataframe['doji_star'] = talib.CDLDOJISTAR(
        dataframe['open'],
        dataframe['high'],
        dataframe['low'],
        dataframe['close']
    )
    # If display is true, add the doji star to the graph
    if display:
        # Add a column to the dataframe which sets the doji_star_value to be the close price of the relevant candle if the value is not zero
        dataframe['doji_star_value'] = dataframe.apply(lambda x: x['close'] if x['doji_star'] != 0 else 0, axis=1)
        # Extract the rows where doji_star_value is not zero
        dataframe = dataframe[dataframe['doji_star_value'] != 0]
        # Add doji star to graph
        fig = display_lib.add_markers_to_graph(
            base_fig=fig,
            dataframe=dataframe,
            value_column='doji_star_value',
            point_names='Doji Star'
        )

    return dataframe
