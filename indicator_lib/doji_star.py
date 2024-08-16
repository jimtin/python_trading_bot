import talib
import display_lib


def doji_star(dataframe, display=False, fig=None):
    """
    Function to calculate the doji star indicator. This is a candlestick pattern, more details can be found here:
    https://medium.com/me/stats/post/28c12f04caf6
    :param dataframe: dataframe object where the Doji Star patterns should be detected on
    :param display: boolean to determine whether the Doji Star patterns should be displayed on the graph
    :param fig: plotly figure object to add the Doji Star patterns to
    :return: dataframe with Doji Star patterns identified
    """
    df = dataframe.copy()
    df['doji_star'] = 0  # Add doji star column
    # Calculate doji star
    df['doji_star'] = talib.CDLDOJISTAR(df['open'], df['high'], df['low'], df['close'])
    if display:  # add the doji star to the graph
        # Add a doji_star_value column to be the close price of the relevant candle if the value is not zero
        df['doji_star_value'] = df.apply(lambda x: x['close'] if x['doji_star'] != 0 else 0, axis=1)
        # Extract the rows where doji_star_value is not zero
        df = df[df['doji_star_value'] != 0]
        # Add doji star to graph
        fig = display_lib.add_markers_to_graph(
            base_fig=fig,
            dataframe=df,
            value_column='doji_star_value',
            point_names='Doji Star'
        )

    return df
