import numpy as np


# Function to identify ema cross events
def ema_cross(dataframe, ema_one, ema_two):
    '''
    Function to identify ema cross events
    :param dataframe: Pandas Dataframe object
    :param ema_one: Column One of EMA cross
    :param ema_two: Column Two of EMA cross
    :return:
    '''
    # Create a position column
    dataframe['position'] = dataframe[ema_one] > dataframe[ema_two]
    # Create a preposition column
    dataframe['pre_position'] = dataframe['position'].shift(1)
    # Get rid of NA values
    dataframe.dropna(inplace=True)
    # Define Crossover events
    dataframe['crossover'] = np.where(dataframe['position'] == dataframe['pre_position'], False, True)
    return dataframe

