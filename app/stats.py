from app import db
from enum import Enum
import pygal
from pygal.style import DarkSolarizedStyle, DefaultStyle
import lxml


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


# SEASON PITCH STATISTICS -----------------------------------------------------
def avgPitchVeloPitcher(pitcher):
    """Calculates pitch velo by outings and season.

    Arguments:
        pitcher {pitcher object} -- pitcher to be analyzed

    Returns:
        tuple -- a dictionary containing avg of all pitches in a season and a
            dictionary containing avg of pitches by outing in season
    """
    outings = []
    pitches_totals = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
    pitches_total_velo_totals = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0}
    pitch_avg_velo_totals = {
        "FB": 0, "CB": 0, "SL": 0,
        "CH": 0, "CT": 0, "SM": 0}

    # get totals for player
    for outing in pitcher.outings:

        pitches = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
        pitches_total_velo = {
            "FB": 0, "CB": 0, "SL": 0,
            "CH": 0, "CT": 0, "SM": 0}
        pitch_avg_velo = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

        # calculate sums
        for at_bat in outing.at_bats:
            for pitch in at_bat.pitches:
                # for season stats
                if pitch.velocity not in [None, ""]:
                    pitches[PitchType(pitch.pitch_type).name] += 1
                    pitches_total_velo[
                        PitchType(pitch.pitch_type).name] += pitch.velocity

                    # for outing specific stats
                    pitches_totals[PitchType(pitch.pitch_type).name] += 1
                    pitches_total_velo_totals[
                        PitchType(pitch.pitch_type).name] += pitch.velocity

        # calculate averages for outings
        for key, val in pitches_totals.items():
            if pitches[key] != 0:
                pitch_avg_velo[key] = truncate(
                    pitches_total_velo[key]/pitches[key])

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

    # calculate averages for season totals
    for key, val in pitches_totals.items():
        if pitches_totals[key] != 0:
            pitch_avg_velo_totals[key] = truncate(
                pitches_total_velo_totals[key]/pitches_totals[key])

    return (pitch_avg_velo_totals, outings)


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
    # storage for season totals data
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

    # iterate through all pitcher appearances and at_bats
    for outing in pitcher.outings:
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

                # for season totals
                pitches_totals[PitchType(pitch.pitch_type).name] += 1
                pitches_totals['total'] += 1

                if (pitch.pitch_result == 'SS' or pitch.pitch_result == 'CS' or
                        pitch.pitch_result == 'F' or pitch.pitch_result == 'IP'):

                    # for outing specific
                    pitches_strikes[PitchType(pitch.pitch_type).name] += 1
                    pitches_strikes['total'] += 1

                    # for season totals
                    pitches_strikes_totals[PitchType(pitch.pitch_type).name] += 1
                    pitches_strikes_totals['total'] += 1

        # Calculate outing totals
        for key, val in pitches.items():
            if pitches[key] != 0:
                pitch_strike_percentage[key] = (
                    truncate(pitches_strikes[key]/pitches[key]*100))

        # place into data array
        outings.append({
            "details": {
                "date": outing.date,
                "opponent": outing.opponent,
                "season": outing.season},
            "percentages": pitch_strike_percentage
        })

    # calculate season totals
    for key, val in pitches_totals.items():
        if pitches_totals[key] != 0:
            pitch_strike_percentage_totals[key] = (
                truncate(pitches_strikes_totals[key]/pitches_totals[key]*100))

    return (pitch_strike_percentage_totals, outings)


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
    # storage for season totals
    num_pitches_total = 0
    pitches_total = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
    pitches_percentages_total = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

    for outing in pitcher.outings:
        # storage for individual outings
        num_pitches = 0
        pitches = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
        pitches_percentages = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

        for at_bat in outing.at_bats:
            for pitch in at_bat.pitches:
                # for outing specific calculations
                pitches[PitchType(pitch.pitch_type).name] += 1
                num_pitches += 1

                # for season totals
                pitches_total[PitchType(pitch.pitch_type).name] += 1
                num_pitches_total += 1

        # calculate values for individual outings
        if num_pitches != 0:
            for key, val in pitches.items():
                pitches_percentages[key] = truncate(pitches[key] / num_pitches * 100)

        # storage array for individual outing totals
        outings.append({
            "details": {
                "date": outing.date,
                "opponent": outing.opponent,
                "season": outing.season},
            "percentages": pitches_percentages,
            "usages": pitches
        })

    # calculate season totals
    if num_pitches_total != 0:
        for key, val in pitches.items():
            pitches_percentages_total[key] = truncate(pitches_total[key] / num_pitches_total * 100)

    # storage array for season totals values
    season = {
        "percentages": pitches_percentages_total,
        "usages": pitches_total
    }

    return (season, outings)


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
