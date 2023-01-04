# Initialize MetaTrader Error
class MetaTraderInitializeError(Exception):
    "MetaTrader 5 Initilization failed. Check username, password, server, path"
    pass


# Login to MetaTrader Error
class MetaTraderLoginError(Exception):
    "Error logging in to MetaTrader"
    pass


# Incorrect symbol provided
class MetaTraderSymbolDoesNotExistError(Exception):
    "One of the provided symbols does not exist"
    pass


# Symbol unable to be enabled
class MetaTraderSymbolUnableToBeEnabledError(Exception):
    "One of the symbols provided was not able to be enabled"
    pass


# Algo Trading enabled on MetaTrader 5
class MetaTraderAlgoTradingNotDisabledError(Exception):
    "Turn AlgoTrading off on MetaTrader terminal to use Python Trading Bot"
    pass


# Error placing order
class MetaTraderOrderPlacingError(Exception):
    "Error placing order on MetaTrader"
    pass


# Error with balance check
class MetaTraderOrderCheckError(Exception):
    "Error checking order on MetaTrader"
    pass


# Error canceling order
class MetaTraderCancelOrderError(Exception):
    "Error canceling order on MetaTrader"
    pass


# Error modifying a position MetaTrader
class MetaTraderModifyPositionError(Exception):
    "Error modifying position on MetaTrader"
    pass


# Error closing a position
class MetaTraderClosePositionError(Exception):
    "Error closing a position on MetaTrader"
    pass


# Error for having a zero stop price on a BUY_STOP or SELL_STOP
class MetaTraderIncorrectStopPriceError(Exception):
    "Cannot have a 0.00 price on a STOP order"
    pass


# Error for zero ticks returned from query
class MetaTraderZeroTicksDownloadedError(Exception):
    "Zero ticks retrieved from MetaTrader 5 Terminal"
    pass


# SQL Error
class SQLTableCreationError(Exception):
    "Error creating SQL table"
    pass

# Backtest error
class BacktestIncorrectBacktestTimeframeError(Exception):
    "Incorrect timeframe selected for backtest timeframe"
    pass
