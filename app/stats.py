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

    for pitch in outing.pitches:
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
                pitches_missed[key]/pitches_swung_at[key] * 100)

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
        "FB": 0,
        "CB": 0,
        "SL": 0,
        "CH": 0,
        "CT": 0,
        "SM": 0,
        "total": 0}
    pitches_strikes = {
        "FB": 0,
        "CB": 0,
        "SL": 0,
        "CH": 0,
        "CT": 0,
        "SM": 0,
        "total": 0}
    pitch_strike_percentage = {
        "FB": 0,
        "CB": 0,
        "SL": 0,
        "CH": 0,
        "CT": 0,
        "SM": 0,
        "total": 0}

    for pitch in outing.pitches:
        pitches[PitchType(pitch.pitch_type).name] += 1
        pitches['total'] += 1
        if (pitch.pitch_result == 'SS' or pitch.pitch_result == 'CS' or
                pitch.pitch_result == 'F' or pitch.pitch_result == 'IP'):
            pitches_strikes[PitchType(pitch.pitch_type).name] += 1
            pitches_strikes['total'] += 1

    for key, val in pitches.items():
        if pitches[key] != 0:
            pitch_strike_percentage[key] = (
                pitches_strikes[key]/pitches[key]*100)

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

    for pitch in outing.pitches:
        if (pitch.velocity):
            pitches[PitchType(pitch.pitch_type).name] += 1
            pitches_total_velo[
                PitchType(pitch.pitch_type).name] += pitch.velocity

    for key, val in pitches.items():
        if pitches[key] != 0:
            pitch_avg_velo[key] = pitches_total_velo[key]/pitches[key]

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
    num_pitches = outing.pitches.count()
    pitches = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}

    for pitch in outing.pitches:
        pitches[PitchType(pitch.pitch_type).name] += 1

    pitch_percentages = {"FB": 0, "CB": 0, "SL": 0, "CH": 0, "CT": 0, "SM": 0}
    if num_pitches != 0:
        for key, val in pitches.items():
            pitch_percentages[key] = pitches[key]/num_pitches * 100

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
    num_pitches = outing.pitches.count()
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
    
    for pitch in outing.pitches:
        count = f"{pitch.count_balls}-{pitch.count_strikes}"
        pitch_type = PitchType(pitch.pitch_type).name

        counts[count]["total"] += 1
        counts[count]["pitches"][pitch_type] += 1

    # create count percentages
    for key, value in counts.items():
        total = value["total"]
        if total != 0:
            for pitch in value["pitches"].keys():
                counts_percentages[key]["pitches"][pitch] = (
                    value["pitches"][pitch]/total * 100)
                counts_percentages[key]["total"] = total/num_pitches
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
    num_pitches = outing.pitches.count()
    line_chart = pygal.Line(
        style=DarkSolarizedStyle,
        title="Velocity changes over time"
    )
    line_chart.x_labels = map(str, range(1, num_pitches+1))
    line_chart.dyanamic_print_values = True

    velocities = {"FB": [], "CB": [], "SL": [], "CH": [], "CT": [], "SM": []}
    for pitch in outing.pitches:
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
        style=DarkSolarizedStyle
    )

    for pitch_type, values in data.items():
        bar_chart.add(pitch_type, values)

    return bar_chart
