from app import db
from enum import Enum
import pygal
from pygal.style import DarkSolarizedStyle, DefaultStyle
import lxml
import math
from app.models import Season, Outing


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


def calcPitchWhiffRate(outing):
    '''
    Calculates the whiff rate by pitch.

    PARAM:
        -outing: Data to be parsed into stats. Should be an
            Outing object

    RETURN:
        -dictionary containing whiff rate by pitch
    '''
    pitches_swung_at = {
        "FB": 0,
        "CB": 0,
        "SL": 0,
        "CH": 0,
        "CT": 0,
        "SM": 0,
        "total": 0}
    pitches_missed = {
        "FB": 0,
        "CB": 0,
        "SL": 0,
        "CH": 0,
        "CT": 0,
        "SM": 0,
        "total": 0}
    pitches_whiff = {
        "FB": 0,
        "CB": 0,
        "SL": 0,
        "CH": 0,
        "CT": 0,
        "SM": 0,
        "total": 0}

    for at_bat in outing.at_bats:
        for pitch in at_bat.pitches:
            if pitch.pitch_result == 'SS':
                pitches_swung_at[PitchType(pitch.pitch_type).name] += 1
                pitches_missed[PitchType(pitch.pitch_type).name] += 1
                pitches_swung_at['total'] += 1
                pitches_missed['total'] += 1
            if pitch.pitch_result == 'F' or pitch.pitch_result == 'IP':
                pitches_swung_at[PitchType(pitch.pitch_type).name] += 1
                pitches_swung_at['total'] += 1
    for key, val in pitches_swung_at.items():
        if (pitches_swung_at[key] != 0):
            pitches_whiff[key] = (
                truncate(pitches_missed[key]/pitches_swung_at[key] * 100))

    return (pitches_whiff)


def calcPitchStrikePercentage(outing):
    '''
    Calculates the strike percentage of each pitch.

    PARAM:
        -outing: the outing to be parsed for data. Should be an
            Outing object

    RETURN:
        -dictionary containing strike percentage by pitch
    '''
    pitches = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0,
        "total": 0}
    pitches_strikes = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0,
        "total": 0}
    pitch_strike_percentage = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0,
        "total": 0}

    for at_bat in outing.at_bats:
        for pitch in at_bat.pitches:
            pitches[PitchType(pitch.pitch_type).name] += 1
            pitches['total'] += 1
            if (pitch.pitch_result == 'SS' or pitch.pitch_result == 'CS' or
                    pitch.pitch_result == 'F' or pitch.pitch_result == 'IP'):
                pitches_strikes[PitchType(pitch.pitch_type).name] += 1
                pitches_strikes['total'] += 1

    for key, val in pitches.items():
        if pitches[key] != 0:
            pitch_strike_percentage[key] = (
                truncate(pitches_strikes[key]/pitches[key]*100))

    return (pitch_strike_percentage)


def calcAverageVelo(outing):
    '''
    Calculates the average velocity of each pitch.

    PARAM:
        -outing: The data to be parsed. Should be an
            Outing object.

    RETURN:
        -dictionary containing decimal average velo by pitch
    '''

    pitches = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
    pitches_total_velo = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
    pitch_avg_velo = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

    for at_bat in outing.at_bats:
        for pitch in at_bat.pitches:
            if (pitch.velocity):
                pitches[PitchType(pitch.pitch_type).name] += 1
                pitches_total_velo[
                    PitchType(pitch.pitch_type).name] += pitch.velocity

    for key, val in pitches.items():
        if pitches[key] != 0:
            pitch_avg_velo[key] = truncate(
                pitches_total_velo[key]/pitches[key])

    return (pitch_avg_velo)


def calcPitchPercentages(outing):
    '''
    Function to calculate percent of time each pitch was thrown.

    PARAM:
        -outing: The outing to be parsed for data. Should be an
            Outing object.

    RETURN:
        -Tuple of (pitches, pitch_percentages).
            "pitches" is a dictionary containing the integer value of each
                pitch throw.
            "pitch_percentages" is a dictionary containing the percent each
                pitch was thrown.
    '''
    num_pitches = 0
    pitches = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

    for at_bat in outing.at_bats:
        for pitch in at_bat.pitches:
            pitches[PitchType(pitch.pitch_type).name] += 1
            num_pitches += 1

    pitch_percentages = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
    if num_pitches != 0:
        for key, val in pitches.items():
            pitch_percentages[key] = truncate(pitches[key]/num_pitches * 100)

    return (pitches, pitch_percentages)
    # Will be in form:
    #       {"FB":0.0, "CB":0.0, "SL":0.0, "CH":0.0, "CT":0.0, "SM":0.0}
    # With each value being 0<=val<=100


def pitchUsageByCount(outing):
    '''
    Creates pitch usage by count statistic sheet.

    PARAM:
        -outing: Outing object to be parsed. Should come from
            Outing.query.filter(...)
    RETURN:
        -tuple object containing (counts, counts_percentages).
            "counts" is a dictionary representing the number of times a pitch
                was thrown.
            "counts_percentages" is a dictionary that represents the
                percentage of time a pitch was thrown by count
    '''
    num_pitches = 0
    # PLEASE COLLAPSE THIS VARIABLE IT'S DUMB
    counts = {
        "0-0": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "0-1": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "0-2": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "1-0": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "1-1": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "1-2": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "2-0": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "2-1": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "2-2": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "3-0": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "3-1": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "3-2": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            }
    }
    counts_percentages = {
        "0-0": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "0-1": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "0-2": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "1-0": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "1-1": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "1-2": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "2-0": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "2-1": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "2-2": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "3-0": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "3-1": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            },
        "3-2": {
            "pitches": {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0},
            "total": 0
            }
    }

    for at_bat in outing.at_bats:
        for pitch in at_bat.pitches:
            count = pitch.count
            pitch_type = PitchType(pitch.pitch_type).name

            counts[count]["total"] += 1
            counts[count]["pitches"][pitch_type] += 1

            num_pitches += 1

    # create count percentages
    for key, value in counts.items():
        total = value["total"]
        if total != 0:
            for pitch in value["pitches"].keys():
                counts_percentages[key]["pitches"][pitch] = (
                    truncate(value["pitches"][pitch]/total * 100))
                counts_percentages[key]["total"] = (
                    truncate(total/num_pitches * 100))
        else:  # case in which there were no pitches thrown in a count
            counts_percentages[key]["pitches"] = counts[key]["pitches"]
            counts_percentages[key]["total"] = 0

    return (counts, counts_percentages)


def createPitchPercentagePieChart(data):
    '''
    Function to create pitch percentage pie chart.

    PARAM:
        -data: Data to be transformed into pie chart. Should be percentage
            return from calcPitchPercentages(...)
    RETURN:
        -pygal pie chart object complete with data
    '''
    pie_chart = pygal.Pie(
        title="Pitch Usage Percentages",
        style=DarkSolarizedStyle(
            value_font_family='googlefont:Raleway',
            value_font_size=30,
            value_colors=('white')
        ),
        height=600,
        width=600,
        explicit_size=True
    )
    pie_chart.dyanamic_print_values = True

    for pitch, value in data.items():
        insert_value = {"value": value, "label": pitch}
        pie_chart.add(pitch, value)

    return pie_chart


def velocityOverTimeLineChart(outing):
    '''
    Function to create the velocity over time line chart from statistics

    PARAM:
        -outing: the single outing to be parsed over. Should come from
            Outing.query.filter()...
    RETURN:
        - pygal line chart object complete with data
    '''
    num_pitches = 0
    for at_bat in outing.at_bats:
        for pitch in at_bat.pitches:
            num_pitches += 1
    line_chart = pygal.Line(
        style=DarkSolarizedStyle,
        title="Velocity changes over time",
        show_minor_x_labels=False,
        truncate_label=3
    )
    line_chart.x_labels = map(str, range(1, num_pitches+1))
    lst = list(range(num_pitches+1))
    line_chart.x_labels_major = lst[0::10]
    line_chart.dyanamic_print_values = True

    velocities = {"FB": [], "CB": [], "SL": [], "CH": [], "CT": [], "SM": []}
    for at_bat in outing.at_bats:
        for pitch in at_bat.pitches:
            pitch_type = PitchType(pitch.pitch_type).name
            for key in velocities.keys():
                if key is pitch_type:
                    velocities[key].append(pitch.velocity)
                else:
                    velocities[key].append(None)

    for pitch_type, pitch_values in velocities.items():
        if pitch_type == "SM":
            line_chart.add("2-SEAM", pitch_values)
        else:
            line_chart.add(pitch_type, pitch_values)

    return line_chart


def pitchStrikePercentageBarChart(data):
    '''
    Function to create the pitch by pitch strike percentage bar chart.

    PARAM:
        -data: Data to be parsed over and turned to chart. Should be
            return data from calcPitchStrikePercentage(...)

    RETURN:
        - pygal bar chart object complete with data
    '''
    bar_chart = pygal.Bar(
        title="Stike Percentage by Pitch",
        style=DarkSolarizedStyle,
        range=(0, 100)
    )

    for pitch_type, values in data.items():
        bar_chart.add(pitch_type, values)

    return bar_chart


def pitchUsageByCountLineCharts(data):
    data_reformat = {
        "FB": {}, "CB": {}, "SL": {}, "CH": {}, "CT": {}, "SM": {}
    }
    for count, dat in data.items():
        for pitch, usage in dat['pitches'].items():
            data_reformat[pitch][count] = usage
    # print(data_reformat)

    line_chart = pygal.Line(
        style=DarkSolarizedStyle,
        title="Pitch Usage by Count"
    )

    line_chart.x_labels = data_reformat["FB"].keys()
    line_chart.dyanamic_print_values = True

    for pitch_type, pitch_data in data_reformat.items():
        line_chart.add(pitch_type, pitch_data.values())

    return line_chart


# UTILITY STAT FUNCTIONS-------------------------------------------------------
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

def getSeasons(pitcher):
    '''
    gets all of the seasons the pitcher has thrown in

    PARAM:
        - pitcher {object}
    
    RETURN:
        - seasons {array} which holds the season objects
    '''
    outings = Outing.query.filter_by(pitcher_id=pitcher.id).all()
    seasons = []
    for outing in outings:
        if outing.season not in seasons:
            seasons.append(outing.season)
    return seasons

# PITCHER ADVANCED STATISTICS -------------------------------------------------
def avgPitchVeloPitcher(pitcher):
    """Calculates pitch velo by outings and season.

    Arguments:
        pitcher {pitcher object} -- pitcher to be analyzed

    Returns:
        tuple -- a dictionary containing avg of all pitches in a season and a
            dictionary containing avg of pitches by outing in season
    """
    # return array for totals by outings
    outings = []

    # used to calculate totals for career
    totals_pitch_num = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0}
    totals_pitch_velo_sum = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0}
    totals_pitch_velo_avg = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0}    
    
    # set up the dictionary to updated based on which season
    seasons = getSeasons(pitcher)
    season_totals = dict()
    for season in seasons:
        name = f"{season.semester} {season.year}"
        season_totals.update({
            name: {
                "pitch_num": {
                    "FB": 0, "CB": 0, "SL": 0,
                    "CH": 0, "CT": 0, "SM": 0},
                "pitch_velo_sum": {
                    "FB": 0, "CB": 0, "SL": 0,
                    "CH": 0, "CT": 0, "SM": 0}
            }
        })
    
    # parse through all the outings for the pitcher
    for outing in pitcher.outings:

        # get the season object and set name variable
        season = Season.query.filter_by(id=outing.season_id).first()
        season_name = f"{season.semester} {season.year}"

        # set up dictionaries for outing avg velo calculations
        pitches = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
        pitches_total_velo = {
            "FB": 0, "CB": 0, "SL": 0,
            "CH": 0, "CT": 0, "SM": 0}
        pitch_avg_velo = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

        # parse through all the pitches of a given outing
        for at_bat in outing.at_bats:
            for pitch in at_bat.pitches:

                # make sure there was a velo reading
                if pitch.velocity not in [None, ""]:

                    # update dictionary values for outing
                    pitches[PitchType(pitch.pitch_type).name] += 1
                    pitches_total_velo[
                        PitchType(pitch.pitch_type).name] += pitch.velocity
                    
                    # update dictionary values for season
                    season_totals[season_name]["pitch_num"][
                        PitchType(pitch.pitch_type).name] += 1
                    season_totals[season_name]["pitch_velo_sum"][
                        PitchType(pitch.pitch_type).name] += pitch.velocity

                    # update dictionary values for career
                    totals_pitch_num[PitchType(pitch.pitch_type).name] += 1
                    totals_pitch_velo_sum[
                        PitchType(pitch.pitch_type).name] += pitch.velocity

        # calculate averages for outings
        for key, val in pitches.items():
            if pitches[key] != 0:
                pitch_avg_velo[key] = truncate(
                    pitches_total_velo[key]/pitches[key], 1)

        # fill in outings arr
        outings.append(
            {
                "details": {
                    "date": outing.date,
                    "opponent": outing.opponent,
                    "season": outing.season},
                "velos": pitch_avg_velo
            }
        )

    # calculate averages for career totals
    for key, val in totals_pitch_num.items():
        if totals_pitch_num[key] != 0:
            totals_pitch_velo_avg[key] = truncate(
                totals_pitch_velo_sum[key]/totals_pitch_num[key], 1)
    
    # calculate averages for season totals
    season_averages = dict()
    for season in seasons:
        name = f"{season.semester} {season.year}"
        averages = {
            name: {
                "FB": 0, "CB": 0, "SL": 0,
                "CH": 0, "CT": 0, "SM": 0
            }
        }
        num = season_totals[name]["pitch_num"]
        velo = season_totals[name]["pitch_velo_sum"]
        for key, val in num.items():
            if num[key] != 0:
                averages[name][key] = truncate(velo[key]/num[key], 1)
        season_averages.update(averages)

    return (totals_pitch_velo_avg, outings, season_averages)


def pitchStrikePercentageSeason(pitcher):
    """Calculates each outing's strike percentage and season totals.

    Arguments:
        pitcher {user object} -- pitcher whose stats are to be analyzed

    Returns:
        [tuple] -- first value contains the season averages for strike
        percentage. the second value contains each outing's strike percentages
        and meta-data as a dictionary
    """
    # storage array for individual outing data
    outings = []

    # storage for career totals data
    pitches_totals = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0,
        "total": 0}
    pitches_strikes_totals = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0,
        "total": 0}
    pitch_strike_percentage_totals = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0,
        "total": 0}
    
    # set up the dictionary to updated based on which season
    seasons = getSeasons(pitcher)
    season_totals = dict()
    for season in seasons:
        name = f"{season.semester} {season.year}"
        season_totals.update({
            name: {
                "pitch_num": {
                    "FB": 0, "CB": 0, "SL": 0,
                    "CH": 0, "CT": 0, "SM": 0,
                    "total": 0},
                "pitch_strikes": {
                    "FB": 0, "CB": 0, "SL": 0,
                    "CH": 0, "CT": 0, "SM": 0,
                    "total": 0},
            }
        })

    # iterate through all pitcher appearances and at_bats
    for outing in pitcher.outings:

        # get the season object and set name variable
        season = Season.query.filter_by(id=outing.season_id).first()
        season_name = f"{season.semester} {season.year}"

        # storage for individual outing calculations
        pitches = {
            "FB": 0, "CB": 0, "SL": 0,
            "CH": 0, "CT": 0, "SM": 0,
            "total": 0}
        pitches_strikes = {
            "FB": 0, "CB": 0, "SL": 0,
            "CH": 0, "CT": 0, "SM": 0,
            "total": 0}
        pitch_strike_percentage = {
            "FB": 0, "CB": 0, "SL": 0,
            "CH": 0, "CT": 0, "SM": 0,
            "total": 0}

        for at_bat in outing.at_bats:
            for pitch in at_bat.pitches:

                # for outing specific
                pitches[PitchType(pitch.pitch_type).name] += 1
                pitches['total'] += 1

                # for career totals
                pitches_totals[PitchType(pitch.pitch_type).name] += 1
                pitches_totals['total'] += 1

                # for season totals
                season_totals[season_name]["pitch_num"][
                    PitchType(pitch.pitch_type).name] += 1
                season_totals[season_name]["pitch_num"][
                    'total'] += 1

                if pitch.pitch_result is not 'B':

                    # for outing specific
                    pitches_strikes[PitchType(pitch.pitch_type).name] += 1
                    pitches_strikes['total'] += 1

                    # for career totals
                    pitches_strikes_totals[PitchType(pitch.pitch_type).name] += 1
                    pitches_strikes_totals['total'] += 1

                    # for season totals
                    season_totals[season_name]["pitch_strikes"][
                        PitchType(pitch.pitch_type).name] += 1
                    season_totals[season_name]["pitch_strikes"][
                        'total'] += 1

        # Calculate outing totals
        for key, val in pitches.items():
            if pitches[key] != 0:
                pitch_strike_percentage[key] = (
                    int(truncate(pitches_strikes[key]/pitches[key]*100, 0)))

        # place into data array
        outings.append({
            "details": {
                "date": outing.date,
                "opponent": outing.opponent,
                "season": outing.season},
            "percentages": pitch_strike_percentage
        })

    # calculate career totals
    for key, val in pitches_totals.items():
        if pitches_totals[key] != 0:
            pitch_strike_percentage_totals[key] = (
                int(truncate(pitches_strikes_totals[key]/pitches_totals[key]*100, 0)))

    # calculate season totals
    season_strike_percentage = dict()
    for season in seasons:
        name = f"{season.semester} {season.year}"
        totals = {
            name: {
                "FB": 0, "CB": 0, "SL": 0,
                "CH": 0, "CT": 0, "SM": 0,
                "total": 0
            }
        }
        num = season_totals[name]["pitch_num"]
        strikes = season_totals[name]["pitch_strikes"]
        for key, val in num.items():
            if num[key] != 0:
                totals[name][key] = int(truncate(100*strikes[key]/num[key], 0))
        season_strike_percentage.update(totals)

    return (pitch_strike_percentage_totals, outings, season_strike_percentage)


def pitchUsageSeason(pitcher):
    """Calculates pitch usage totals and percentages for a pitcher by outing
    
    Arguments:
        pitcher {User object} -- pitcher to be analyzed
    
    Returns:
        [tuple] -- first value is a dictionary that contains season totals and
        percentages. the second is a dictionary that contains outing specific
        meta-data, percentages, and totals
    """    
    # return array array for outing specific
    outings = []
    # storage for career totals
    num_pitches_total = 0
    pitches_total = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
    pitches_percentages_total = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

    # set up the dictionary to updated based on which season
    seasons = getSeasons(pitcher)
    season_totals = dict()
    for season in seasons:
        name = f"{season.semester} {season.year}"
        season_totals.update({
            name: {
                "pitch_num": {
                    "FB": 0, "CB": 0, "SL": 0,
                    "CH": 0, "CT": 0, "SM": 0},
                "total": 0
            }
        })


    for outing in pitcher.outings:
        # storage for individual outings
        num_pitches = 0
        pitches = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
        pitches_percentages = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

        # get the season object and set name variable
        season = Season.query.filter_by(id=outing.season_id).first()
        season_name = f"{season.semester} {season.year}"

        for at_bat in outing.at_bats:
            for pitch in at_bat.pitches:
                # for outing specific calculations
                pitches[PitchType(pitch.pitch_type).name] += 1
                num_pitches += 1

                # for career totals
                pitches_total[PitchType(pitch.pitch_type).name] += 1
                num_pitches_total += 1

                # for season totals
                season_totals[season_name]["pitch_num"][
                    PitchType(pitch.pitch_type).name] += 1
                season_totals[season_name]["total"] += 1


        # calculate values for individual outings
        if num_pitches != 0:
            for key, val in pitches.items():
                pitches_percentages[key] = int(truncate(pitches[key] / num_pitches * 100, 0))

        # storage array for individual outing totals
        outings.append({
            "details": {
                "date": outing.date,
                "opponent": outing.opponent,
                "season": outing.season},
            "percentages": pitches_percentages,
            "usages": pitches
        })

    # calculate career totals
    if num_pitches_total != 0:
        for key, val in pitches.items():
            pitches_percentages_total[key] = int(truncate(pitches_total[key] / num_pitches_total * 100, 0))

    # storage array for career totals values
    career = {
        "percentages": pitches_percentages_total,
        "usages": pitches_total
    }

    # calculate season totals
    season_percentages = dict()
    for season in seasons:
        name = f"{season.semester} {season.year}"
        totals = {
            name: {
                "FB": 0, "CB": 0, "SL": 0,
                "CH": 0, "CT": 0, "SM": 0,
            }
        }
        num = season_totals[name]["pitch_num"]
        total = season_totals[name]["total"]
        for key, val in num.items():
            if num[key] != 0:
                totals[name][key] = int(truncate(100*num[key]/total, 0))
        season_percentages.update(totals)
    
    # storage array for season totals
    season_percentages_usages = {
        "percentages": season_percentages,
        "usages": season_totals
    }

    return (career, outings, season_percentages_usages)


# PITCHER BASIC STATISTICS ----------------------------------------------------
def seasonStatLine(pitcher):
    """Calculates regular stat line for the pitcher desired outing by outing
    and as a career total.

    Arguments:
        pitcher {user object} -- pitcher whose stats are to be analyzed

    Returns:
        [tuple] -- first is a dictionary containing the career total stat line.
        The second value is an array containing dicts containing the meta data
        associated with each outing, as well as its stat line.
    """
    outings = []
    # Player total statline
    stat_line_total = {
        "ip": 0.0, "h": 0, "bb": 0, "hbp": 0, "e": 0, "k": 0, "kl": 0, "1b": 0,
        "2b": 0, "3b": 0, "hr": 0, "kp9": 0.0, "bb9": 0.0, "p": 0, "bf": 0
    }
    for outing in pitcher.outings:

        # Outing specific storage array
        stat_line = {
            "ip": 0.0, "h": 0, "bb": 0, "hbp": 0, "e": 0, "k": 0, "kl": 0,
            "1b": 0, "2b": 0, "3b": 0, "hr": 0, "kp9": 0.0, "bb9": 0.0, "p": 0,
            "bf": 0
        }
        for at_bat in outing.at_bats:
            for pitch in at_bat.pitches:
                stat_line['p'] += 1  # increase pitches

                # check ball in play or out statistics
                if pitch.ab_result is not '':
                    stat_line["bf"] += 1  # increase batters faced

                    # stats that result in hit
                    if pitch.ab_result in ["1B", "2B", "3B", "HR"]:
                        stat_line["h"] += 1  # increase hits
                        stat_line[pitch.ab_result.lower()] += 1  # increase type of hit

                    # stats that result in out
                    if pitch.ab_result in ["IP->Out", "K", "KL", "FC", "D3->Out"]:
                        stat_line["ip"] += 1

                        # for outs that were strikeouts
                        if pitch.ab_result in ["K", "KL"]:
                            stat_line[pitch.ab_result.lower()] += 1

                    # stats where batter reaches base another way
                    if pitch.ab_result in ["BB", "HBP", "Error", "CI", "D3->Safe"]:

                        if pitch.ab_result in ["Error", "CI", "D3->Safe"]:
                            stat_line["e"] += 1
                            if pitch.ab_result in ["D3->Safe"]:
                                stat_line["k"] += 1
                        else:
                            stat_line[pitch.ab_result.lower()] += 1

        # fix innings pitched
        stat_line_total["ip"] += stat_line["ip"]
        stat_line["ip"] = truncate(stat_line["ip"] / 3)

        # calculate outing based stats
        if stat_line["ip"] == 0:
            stat_line["kp9"] = "inf"
            stat_line["bb9"] = "inf"
        else:
            stat_line["kp9"] = truncate((stat_line["k"]+stat_line["kl"])/stat_line["ip"] * 9)
            stat_line["bb9"] = truncate(stat_line["bb"]/stat_line["ip"]*9)

        # add to outings return arr
        outings.append({
            "details": {
                "date": outing.date,
                "opponent": outing.opponent,
                "season": outing.season},
            "stat_line": stat_line
        })

        # add to season total stat line
        for stat, val in stat_line.items():
            if stat not in ["kp9", "bb9", "ip"]:
                stat_line_total[stat] += val

    # calc season based summary stats
    stat_line_total["ip"] = truncate(stat_line_total["ip"]/3)
    if(stat_line_total["ip"] > 0):
        stat_line_total["kp9"] = truncate((stat_line_total["k"]+stat_line_total["kl"])/stat_line_total["ip"] * 9)
        stat_line_total["bb9"] = truncate(stat_line_total["bb"]/stat_line_total["ip"]*9)

    return(stat_line_total, outings)


# STAFF BASIC STATISTICS ------------------------------------------------------
def staffBasicStats(pitchers):
    """Generates basic stat line for group of pitchers passed in

    Arguments:
        pitchers {array} -- array of pitcher objects to be analyzed as a staff

    Returns:
        [tuple] -- first is a dictionary containing the staff total stat line.
        The second value is an array containing dicts containing the meta data
        associated with each pitcher, as well as their stat line.
    """
    players = []
    stat_line_total = {
        "ip": 0.0, "h": 0, "bb": 0, "hbp": 0, "e": 0, "k": 0, "kl": 0, "1b": 0,
        "2b": 0, "3b": 0, "hr": 0, "kp9": 0.0, "bb9": 0.0, "p": 0, "bf": 0
    }

    for pitcher in pitchers:
        stat_line = {
            "ip": 0.0, "h": 0, "bb": 0, "hbp": 0, "e": 0, "k": 0, "kl": 0, "1b": 0,
            "2b": 0, "3b": 0, "hr": 0, "kp9": 0.0, "bb9": 0.0, "p": 0, "bf": 0
        }
        for outing in pitcher.outings:
            for at_bat in outing.at_bats:
                for pitch in at_bat.pitches:
                    stat_line['p'] += 1  # increase pitches

                    # check ball in play or out statistics
                    if pitch.ab_result is not '':
                        stat_line["bf"] += 1  # increase batters faced

                        # stats that result in hit
                        if pitch.ab_result in ["1B", "2B", "3B", "HR"]:
                            stat_line["h"] += 1  # increase hits
                            stat_line[pitch.ab_result.lower()] += 1  # increase type of hit

                        # stats that result in out
                        if pitch.ab_result in ["IP->Out", "K", "KL", "FC", "D3->Out"]:
                            stat_line["ip"] += 1

                            # for outs that were strikeouts
                            if pitch.ab_result in ["K", "KL"]:
                                stat_line[pitch.ab_result.lower()] += 1

                        # stats where batter reaches base another way
                        if pitch.ab_result in ["BB", "HBP", "Error", "CI", "D3->Safe"]:

                            if pitch.ab_result in ["Error", "CI", "D3->Safe"]:
                                stat_line["e"] += 1
                            else:
                                stat_line[pitch.ab_result.lower()] += 1

        # sum up a pitchers work to team total
        for stat, val in stat_line.items():
            if stat not in ["kp9", "bb9"]:
                stat_line_total[stat] += val

        # fix ip for player
        stat_line["ip"] = truncate(stat_line["ip"] / 3)

        # calculate ip based stats for pitcher
        if stat_line["ip"] == 0:
            stat_line["kp9"] = "inf"
            stat_line["bb9"] = "inf"
        else:
            stat_line["kp9"] = truncate((stat_line["k"]+stat_line["kl"])/stat_line["ip"] * 9)
            stat_line["bb9"] = truncate(stat_line["bb"]/stat_line["ip"]*9)

        # append to storage array
        players.append({
            "details": {
                "name": f"{pitcher.name}",
                "class": pitcher.grad_year,
                "throws": pitcher.throws},
            "stat_line": stat_line
        })

    # calculate weighted team stat totals
    stat_line_total["ip"] = truncate(stat_line_total["ip"]/3)
    if(stat_line_total["ip"] > 0):
        stat_line_total["kp9"] = truncate((stat_line_total["k"]+stat_line_total["kl"])/stat_line_total["ip"] * 9)
        stat_line_total["bb9"] = truncate(stat_line_total["bb"]/stat_line_total["ip"]*9)

    return (stat_line_total, players)


# STAFF ADVANCED STATISTICS ---------------------------------------------------
def staffPitcherAvgVelo(pitchers):
    """Generates staff average velo's by pitcher, and team averages.

    Arguments:
        pitchers {array} -- array of user objects to be analyzed

    Returns:
        tuple -- first value is a dictionary containing team average velo's by
        pitch, the second is an array of dictionaries containing each
        pitcher's average velo's by pitch, as well as related meta-date
    """
    players = []

    pitches_totals = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
    pitches_total_velo_totals = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0}
    pitch_avg_velo_totals = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

    for pitcher in pitchers:

        # Individual pitcher velo storage
        pitches = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
        pitches_total_velo = {
            "FB": 0, "CB": 0, "SL": 0,
            "CH": 0, "CT": 0, "SM": 0}
        pitch_avg_velo = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

        for outing in pitcher.outings:
            for at_bat in outing.at_bats:
                for pitch in at_bat.pitches:
                    if pitch.velocity not in [None, ""]:
                        # for pitcher individual stats
                        pitches[PitchType(pitch.pitch_type).name] += 1
                        pitches_total_velo[PitchType(pitch.pitch_type).name] += pitch.velocity

                        # for team total stats
                        pitches_totals[PitchType(pitch.pitch_type).name] += 1
                        pitches_total_velo_totals[
                            PitchType(pitch.pitch_type).name] += pitch.velocity

        # calculate averages for pitcher
        for key, val in pitches.items():
            if pitches[key] != 0:
                pitch_avg_velo[key] = truncate(
                    pitches_total_velo[key]/pitches[key])

        # fill in players arr
        players.append(
            {
                "details": {
                    "name": f"{pitcher.name}",
                    "class": pitcher.grad_year,
                    "throws": pitcher.throws},
                "velos": pitch_avg_velo
            }
        )

    # calculate weighted averages for team totals
    for key, val in pitches_totals.items():
        if pitches_totals[key] != 0:
            pitch_avg_velo_totals[key] = truncate(
                pitches_total_velo_totals[key]/pitches_totals[key])

    # calculate unweighted averages for team totals
    # for player in players:
    #     for pitch, val in player["velos"].items():
    #         pitch_avg_velo_totals[pitch] += val
    # for pitch, val in pitch_avg_velo_totals.items():
    #     pitch_avg_velo_totals[pitch] = truncate(pitch_avg_velo_totals[pitch] / len(players))

    return (pitch_avg_velo_totals, players)


def staffPitchStrikePercentage(pitchers):

    # storage array for staff info
    players = []

    # storage for team totals
    pitches_totals = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0,
        "total": 0}
    pitches_strikes_totals = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0,
        "total": 0}
    pitch_strike_percentage_totals = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0,
        "total": 0}

    for pitcher in pitchers:

        # storage for pitchers individual stats
        pitches = {
            "FB": 0, "CB": 0, "SL": 0,
            "CH": 0, "CT": 0, "SM": 0,
            "total": 0}
        pitches_strikes = {
            "FB": 0, "CB": 0, "SL": 0,
            "CH": 0, "CT": 0, "SM": 0,
            "total": 0}
        pitch_strike_percentage = {
            "FB": 0, "CB": 0, "SL": 0,
            "CH": 0, "CT": 0, "SM": 0,
            "total": 0}

        for outing in pitcher.outings:
            for at_bat in outing.at_bats:
                for pitch in at_bat.pitches:
                    # for pitcher specific
                    pitches[PitchType(pitch.pitch_type).name] += 1
                    pitches['total'] += 1

                    # for team totals
                    pitches_totals[PitchType(pitch.pitch_type).name] += 1
                    pitches_totals['total'] += 1

                    if (pitch.pitch_result == 'SS' or pitch.pitch_result == 'CS' or
                            pitch.pitch_result == 'F' or pitch.pitch_result == 'IP'):

                        # for pitcher specific
                        pitches_strikes[PitchType(pitch.pitch_type).name] += 1
                        pitches_strikes['total'] += 1

                        # for team totals
                        pitches_strikes_totals[PitchType(pitch.pitch_type).name] += 1
                        pitches_strikes_totals['total'] += 1

        # Calculate pitcher totals
        for key, val in pitches.items():
            if pitches[key] != 0:
                pitch_strike_percentage[key] = (
                    truncate(pitches_strikes[key]/pitches[key]*100))

        players.append({
            "details": {
                "name": f"{pitcher.name}",
                "class": pitcher.grad_year,
                "throws": pitcher.throws},
            "percentages": pitch_strike_percentage
        })

    # calculate weighted team totals
    for key, val in pitches_totals.items():
        if pitches_totals[key] != 0:
            pitch_strike_percentage_totals[key] = (
                truncate(pitches_strikes_totals[key]/pitches_totals[key]*100))

    # calculate unweighted team totals
    # for player in players:
    #     for pitch, val in player["percentages"].items():
    #         pitch_strike_percentage_totals[pitch] += val
    # for pitch, val in pitch_strike_percentage_totals.items():
    #     pitch_strike_percentage_totals[pitch] = truncate(val / len(players))

    return (pitch_strike_percentage_totals, players)


def outingPitchStatistics(outing):
    '''
    Calculates different statistics for specific pitches for a specific outing

    PARAM:
        - outing (object) - takes in an outing object to look through its pitches
    
    RETURN:
        - array where each index is a pitch which holds different statistics

    '''
    pitch_stats = []
    pitches = [1,7,2,3,4,5]

    for pitch in pitches:
        total_pitches = 0
        num_thrown = 0
        total_velo = 0
        num_with_velo = 0
        velo_max = 0
        velo_min = 150
        num_strikes = 0
        for ab in outing.at_bats:
            for p in ab.pitches:
                total_pitches += 1
                if p.pitch_type is pitch:
                    num_thrown += 1
                    if p.velocity not in [None, ""]:
                        total_velo += p.velocity
                        num_with_velo += 1
                        if p.velocity > velo_max:
                            velo_max = p.velocity
                        if p.velocity < velo_min:
                            velo_min = p.velocity
                    if p.pitch_result is not "B":
                        num_strikes += 1
        
        if num_thrown is 0:
            num_thrown = "X"
            strike_percentage = "X"
        else: 
            strike_percentage = percentage(num_strikes/num_thrown, 0)

        if num_with_velo is not 0:
            velo_avg = truncate(total_velo/num_with_velo, 1)
        else:
            velo_avg = "X"

        if velo_max is 0:
            velo_max = "X"

        if velo_min is 150:
            velo_min = "X"

        if num_thrown not in [0,"X"]:
            percentage_thrown = percentage(num_thrown/total_pitches, 0)
        else:
            percentage_thrown = "X"

        pitch_stats.append(
            {
                "pitch_type": PitchType(pitch).name,
                "num_thrown": num_thrown,
                "velo_avg": velo_avg,
                "velo_max": velo_max,
                "velo_min": velo_min,
                "percentage_thrown": percentage_thrown,
                "strike_percentage": strike_percentage,
            }
        )

    return pitch_stats


def outingTimeToPlate(outing):
    '''
    Calculates time to plate info for a specific outing

    PARAM:
        - outing (object) which has the time to plate info
    
    RETURN:
        - array holding each lead runner and the info associated
            with each situation
    '''
    lead_runners = [1,2,3]
    time_to_plate = []
    for runner in lead_runners:
        total_time = 0
        num_times = 0
        for ab in outing.at_bats:
            for p in ab.pitches:
                if p.lead_runner is runner:
                    if p.time_to_plate not in [None, ""]:
                        total_time += p.time_to_plate
                        num_times += 1
        if num_times is 0:
            num_times = "X"
            avg = "X"
        else:
            avg = truncate(total_time/num_times)
        time_to_plate.append(
            {
                "lead_runner": runner,
                "num_times": num_times,
                "avg": avg,
            }
        )
    return time_to_plate


def veloOverTime(outing):
    velos = {"FB": [], "CB": [], "SL": [], "CH": [], "CT": [], "SM": []}
    for at_bat in outing.at_bats:
        for pitch in at_bat.pitches:
            pitch_type = PitchType(pitch.pitch_type).name
            for key in velos.keys():
                if key is pitch_type:
                    if not pitch.velocity:
                        velos[key].append("null")
                    else:
                        velos[key].append(pitch.velocity)
                else:
                    velos[key].append("null")
    return velos


def teamImportantStatsSeason(pitchers): 
    # weighted strike percentage
    strikes = 0
    total_pitches = 0
    strike_percentage = 0
    # weighted FPS
    first_pitch_strikes = 0
    first_pitches = 0
    fps_percentage = 0 
    # K/BB Ratio
    strikeouts = 0
    walks = 0
    k_to_bb = 0

    for p in pitchers:
        for o in p.outings:
            current_inning = 1
            season = Season.query.filter_by(id=o.season_id).first()
            if season.current_season:
                for ab in o.at_bats:
                    for index, p in enumerate(ab.pitches):
                        total_pitches += 1
                        if p.pitch_result is not "B":
                            strikes += 1 
                        if index is 0:
                            first_pitches += 1
                            if p.pitch_result is not "B":
                                first_pitch_strikes += 1
                        if p.ab_result in ["K", "KL"]:
                            strikeouts += 1
                        if p.ab_result == "BB":
                            walks += 1

    if total_pitches is 0:
        strike_percentage = "X"
    else:
        strike_percentage = percentage(strikes/total_pitches, 0)
    
    if first_pitch_strikes is 0:
        fps_percentage = "X"
    else:
        fps_percentage = percentage(first_pitch_strikes/first_pitches)
    
    if walks is 0:
        if strikeouts is 0:
            k_to_bb = 0
        else: 
            k_to_bb = "inf"
    else:
        k_to_bb = truncate(strikeouts/walks, 1)

    return strike_percentage, fps_percentage, k_to_bb


def batterSwingWhiffRatebyPitchbyCount(batter, seasons=[]):
    pitches_per_count = {
        "0-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "0-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "0-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0}
    }
    swings_per_count = {
        "0-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "0-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "0-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0}
    }
    whiffs_per_count = {
        "0-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "0-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "0-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0}
    }
    swing_rate_by_count = {
        "0-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "0-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "0-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0}
    }
    whiff_rate_by_count = {
        "0-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "0-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "0-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "1-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "2-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-0": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-1": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0},
        "3-2": {"FB": 0, "SM": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0}
    }

    for at_bat in batter.at_bats:
        # check to see if at_bat is in the season(s) we want
        if (len(seasons) is 0) or at_bat.get_season().id in seasons or str(at_bat.get_season().id) in seasons:
            for pitch in at_bat.pitches:
                pitches_per_count[pitch.count][PitchType(pitch.pitch_type).name] += 1

                if pitch.pitch_result in ["SS", "F", "IP"]:
                    swings_per_count[pitch.count][PitchType(pitch.pitch_type).name] += 1
                    if pitch.pitch_result in ["SS"]:
                        whiffs_per_count[pitch.count][PitchType(pitch.pitch_type).name] += 1

    # calculate batter totals
    for count, val in pitches_per_count.items():
        for pitch, num in val.items():
            # calculate swing rate
            if val[pitch] != 0:
                swing_rate_by_count[count][pitch] = truncate(swings_per_count[count][pitch] / val[pitch])

                # calculate whiff rate
                if swings_per_count[count][pitch] != 0:
                    whiff_rate_by_count[count][pitch] = truncate(whiffs_per_count[count][pitch] / swings_per_count[count][pitch])

    return (swing_rate_by_count, whiff_rate_by_count)
