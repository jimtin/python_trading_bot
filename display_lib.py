from sql_lib import sql_interaction
import plotly.graph_objects as go
from dash import Dash, html, dcc
from plotly.subplots import make_subplots


def show_data(table_name, dataframe, graph_name, project_settings):
    """retrieve back_test data and then display chart of close values"""
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
    ))

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
        dcc.Graph(id='Example Graph', figure=fig)
    ])
    app.run_server(debug=True)


def display_graph(plotly_fig, graph_title, dash=False, upload=False):
    """
    Function to display a plotly graph using Dash
    :param plotly_fig: plotly figure
    :param graph_title: string
    :return: None
    """
    # Add in autoscaling for each plotly figure
    plotly_fig.update_layout(autosize=True)
    plotly_fig.update_yaxes(automargin=True)
    plotly_fig.update_layout(xaxis_rangeslider_visible=False)

    if dash:
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
        app.run_server(debug=True)
    else:
        plotly_fig.show()


def display_backtest(original_strategy, strategy_with_trades, table, graph_title):
    original_strategy.update_layout(autosize=True)
    original_strategy.update_yaxes(automargin=True)
    original_strategy.update_layout(xaxis_rangeslider_visible=False)
    app = Dash(__name__)

    # Construct view
    app.layout = html.Div(children=[
        html.H1(graph_title),
        html.Div([
            html.H1(children="Strategy With Trades"),
            html.Div(children='''Original Strategy'''),
            dcc.Graph(
                id="strat_with_trades",
                figure=strategy_with_trades,
                style={'height': '100vh'}
            )
        ]),
        html.Div([
            html.H1(children="Table of Trades"),
            html.Div(children='''Original Strategy'''),
            dcc.Graph(
                id="table_trades",
                figure=table
            )
        ])
    ])

    app.run_server(debug=True)


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


# Function to turn a dataframe into a table
def add_dataframe(dataframe):
    fig = go.Figure(data=[go.Table(
        header=dict(values=["Time", "Order Type", "Stop Price", "Stop Loss", "Take Profit"], align='left'),
        cells=dict(values=[
            dataframe['human_time'],
            dataframe['order_type'],
            dataframe['stop_price'],
            dataframe['stop_loss'],
            dataframe['take_profit']])
    )])
    return fig


def add_trades_to_graph(trades_dict, base_fig):
    point_plot = []
    buy_color = dict(color="green")
    sell_color = dict(color="red")
    # Add each set of trades
    trades = trades_dict["full_trades"]
    for trade in trades:
        if trade['trade_outcome']['not_completed'] is False:
            if trade['trade_type'] == "BUY_STOP":
                color = buy_color
            else:
                color = sell_color

            base_fig.add_trace(
                go.Scatter(
                    x=[trade['order_time'], trade['open_time'], trade['close_time']],
                    y=[trade['order_price'], trade['open_price'], trade['close_price']],
                    name=trade['name'],
                    legendgroup=trade['trade_type'],
                    line=color
                )
            )
    return base_fig
