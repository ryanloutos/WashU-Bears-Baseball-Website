import lxml
import math
import pygal

from app import db

from enum import Enum

from app.models import Game
from app.models import Batter
from app.models import Outing
from app.models import Season

from pygal.style import DefaultStyle
from pygal.style import DarkSolarizedStyle


# ***************-USEFUL ITEMS-*************** #
class PitchType(Enum):
    '''
    Enum that is helpful in translating pitch types easier.
    '''
    FB = 1
    CB = 2
    SL = 3
    CH = 4
    CT = 5
    SM = 7


def truncate(n, decimals=2):
    """Truncates the passed value to decimal places.

    Arguments:
        n {number} -- Number to be truncated

    Keyword Arguments:
        decimals {int} -- Number of decimal places to truncate to(default: {2})

    Returns:
        [int] -- truncated verison of passed value
    """
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def zero_division_handler(n, d):
    return n / d if d else 0


def percentage(n, decimals=0):
    '''
    Gets the percentage rounded to a specific decimal place
    PARAM:
        - n - is a the decimal number 0<=n<=1
        - decimals - is the place you want to round to
    '''
    multiplier = 10 ** decimals
    percentage = 100 * n
    return int(math.floor(percentage*multiplier + 0.5) / multiplier)


class zone_constants:
    # x plane coords
    x_left = -2
    x_zone_left = -0.833
    x_zone_left_third = -0.277
    x_zone_middle = 0
    x_zone_right_third = 0.277
    x_zone_right = 0.833
    x_right = 2
    # y plane coords
    y_top = 4
    y_zone_top = 3.4
    y_zone_upper_third = 2.85
    y_zone_middle = 2.575
    y_zone_lower_third = 2.3
    y_zone_bottom = 1.75
    y_bottom = 0


# Create object of above type
ZONE_CONSTANTS = zone_constants()


def get_zone_region(pitch):
    """Gets the region of the zone that the pitch was in based on the 
    coordinated defined in the zone constants object, which related to
    the js file d3_strikezone.js"""

    if pitch.loc_x in ["", None] or pitch.loc_y in ["", None]:
        return None

    #  x grid region
    if(pitch.loc_x < ZONE_CONSTANTS.x_zone_left):
        x_coord = 0
    elif(pitch.loc_x < ZONE_CONSTANTS.x_zone_left_third):
        x_coord = 1
    elif(pitch.loc_x < ZONE_CONSTANTS.x_zone_right_third):
        x_coord = 2
    elif(pitch.loc_x < ZONE_CONSTANTS.x_zone_right):
        x_coord = 3
    else:
        x_coord = 4

    # Y grid region
    if(pitch.loc_y > ZONE_CONSTANTS.y_zone_top):
        y_coord = 0
    elif(pitch.loc_y > ZONE_CONSTANTS.y_zone_upper_third):
        y_coord = 1
    elif(pitch.loc_y > ZONE_CONSTANTS.y_zone_lower_third):
        y_coord = 2
    elif(pitch.loc_y > ZONE_CONSTANTS.y_zone_bottom):
        y_coord = 3
    else:
        y_coord = 4

    return f"{x_coord}{y_coord}"
