import plotly.subplots

from sql_lib import sql_interaction
import pandas
import plotly.graph_objects as go
from dash import Dash, html, dcc
import chart_studio


# Function to retrieve back_test data and then display chart of close values
def show_data(table_name, dataframe, graph_name, project_settings):
    # Table Name
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
                y=dataframe['ta_sma_200'],
                name='ta_sma_200'
            )
    )

    fig.add_trace(go.Scatter(
        x=dataframe['human_time'],
        y=dataframe['ta_ema_200'],
        name='ta_ema_200'
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['human_time'],
        y=dataframe['ta_ema_15'],
        name='ta_ema_15'
    ))

    # Create Dash
    app = Dash(__name__)
    app.layout = html.Div(children=[
        html.H1(children=graph_name),
        html.Div("Example data"),
        dcc.Graph(
            id='Example Graph',
            figure=fig
        )
    ])
    app.run_server(debug=True)


# Function to display a plotly graph in dash
def display_graph(plotly_fig, graph_title, project_settings=[], dash=False, upload=False):
    """
    Function to display a plotly graph using Dash
    :param plotly_fig: plotly figure
    :param graph_title: string
    :return: None
    """
    # Add in autoscaling
    plotly_fig.update_layout(
        autosize=True,
        height=1000
    )
    plotly_fig.update_yaxes(automargin=True)

    if dash:
        # Create the Dash object
        app = Dash(__name__)
        # Construct view
        app.layout = html.Div(children=[
            html.H1(children=graph_title),
            html.Div("Created by James Hinton from Creative Appnologies"),
            dcc.Graph(
                id=graph_title,
                figure=plotly_fig
            )
        ])
        # Run the image
        app.run_server(debug=True)
    elif upload:
        chart_studio.tools.set_credentials_file(
            username=project_settings['plotly']['username'],
            api_key=project_settings['plotly']['api_key']
        )
        chart_studio.plotly.plot(plotly_fig,file_name="Test", auto_open=True)
    else:
        plotly_fig.show()


# Function to construct base candlestick graph
def construct_base_candlestick_graph(dataframe, candlestick_title):
    """
    Function to construct base candlestick graph
    :param candlestick_title: String
    :param dataframe: Pandas dataframe object
    :return: plotly figure
    """
    # Construct the figure
    fig = go.Figure(data=[go.Candlestick(
        x=dataframe['human_time'],
        open=dataframe['open'],
        high=dataframe['high'],
        close=dataframe['close'],
        low=dataframe['low'],
        name=candlestick_title
    )])
    # Return the graph object
    return fig


# Function to add a line trace to a plot
def add_line_to_graph(base_fig, dataframe, dataframe_column, line_name):
    """
    Function to add a line to trace to an existing figure
    :param base_fig: plotly figure object
    :param dataframe: pandas dataframe
    :param dataframe_column: string of column to plot
    :param line_name: string title of line trace
    :return: updated plotly figure
    """
    # Construct trace
    base_fig.add_trace(go.Scatter(
        x=dataframe['human_time'],
        y=dataframe[dataframe_column],
        name=line_name
    ))
    # Return the object
    return base_fig


# Function to display points on graph as diamond
def add_markers_to_graph(base_fig, dataframe, value_column, point_names):
     """
     Function to add points to a graph
     :param base_fig: plotly figure
     :param dataframe: pandas dataframe
     :param value_column: value for Y display
     :param point_names: what's being plotted
     :return: updated plotly figure
     """
     # Construct trace
     base_fig.add_trace(go.Scatter(
         mode="markers",
         marker=dict(size=8, symbol="diamond"),
         x=dataframe['human_time'],
         y=dataframe[value_column],
         name=point_names
     ))
     return base_fig


# Function to add trades to graph
def add_trades_to_graph(trades, base_fig=None, display_on_base=True):
    # Create a point plot list
    point_plot = []
    # Create the colors
    buy_color = dict(color="green")
    sell_color = dict(color="red")
    # Add each set of trades
    for trade in trades:
        if trade['trade_type'] == "BUY_STOP":
            color = buy_color
        else:
            color = sell_color
        point_plot.append(
            go.Scatter(
                x=[trade['open_time'], trade['close_time']],
                y=[trade['open_price'], trade['close_price']],
                name=trade['name'],
                legendgroup=trade['trade_type'],
                line=color
            )
        )
    if display_on_base:
        if not base_fig:
            base_fig.add_trace(point_plot)
            return base_fig
        else:
            raise ValueError("Base Fig cannot be null for display on base selection")
    else:
        trade_fig = go.Figure(data=point_plot)
        return trade_fig


def backtest_display(prices, trades, balance, title):
    # Construct the graph with subplots
    fig = plotly.subplots.make_subplots(rows=3, cols=1)
    # Add the base graph
    fig.add_trace(prices, row=1, col=1)
    # Add Trades separately
    fig.add_trace(trades, row=2, col=1)
    # Display
    display_graph(fig, title, dash=True)

