from app import db
from enum import Enum
import pygal
from pygal.style import DarkSolarizedStyle, DefaultStyle
import lxml
import math
from app.models import Season, Outing, Game, Batter


# ***************-USEFUL FUNCTIONS-*************** # 
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


def zone_division_stats_batter(batter):
    top_half_pitches = []
    bottom_half_pitches = []

    off_3b_pitches = []
    inner_third_pitches = []
    middle_third_pitches = []
    outer_third_pitches = []
    off_1b_pitches = []

    for at_bat in batter.at_bats:
        for pitch in at_bat.pitches:
            if pitch.loc_x is None or pitch.loc_y is None:
                continue
            x_coord = pitch.loc_x
            y_coord = pitch.loc_y

            # Divide pitches into top half and bottom half of zone
            if y_coord > 2.575:
                top_half_pitches.append(pitch)
            else:
                bottom_half_pitches.append(pitch)

            # Divide pitches into off plate 3b, inner third, middle third, outer third, off plate 1b
            if x_coord < -0.866:   # off plate 3b
                off_3b_pitches.append(pitch)
            elif x_coord < -0.277:
                inner_third_pitches.append(pitch)
            elif x_coord < 0.277:
                middle_third_pitches.append(pitch)
            elif x_coord < 0.8:
                outer_third_pitches.append(pitch)
            else:
                off_1b_pitches.append(pitch)

    # come up with percentages for each zone section
    stats = {
        "top_half_pitches": zone_section_stats_helper(top_half_pitches),
        "bottom_half_pitches": zone_section_stats_helper(bottom_half_pitches),

        "3b_side_pitches": zone_section_stats_helper(off_3b_pitches),
        "1b_side_pitches": zone_section_stats_helper(off_1b_pitches),
        "inner_third_pitches": zone_section_stats_helper(inner_third_pitches),
        "middle_third_pitches": zone_section_stats_helper(middle_third_pitches),
        "outer_third_pitches": zone_section_stats_helper(outer_third_pitches)
    }

    return stats


def zone_section_stats_helper(zone):
    stats = {
        "all": {
            "counters": {
                "num_pitches": len(zone),
                "FB": 0,
                "CB": 0,
                "SL": 0,
                "SM": 0,
                "CH": 0,
                "CT": 0
            },
            "swing_whiff": {
                "swing_rate": 0,
                "whiff_rate": 0,
                "fb_swing_rate": 0,
                "fb_whiff_rate": 0,
                "cb_swing_rate": 0,
                "cb_whiff_rate": 0,
                "sl_swing_rate": 0,
                "sl_whiff_rate": 0,
                "sm_swing_rate": 0,
                "sm_whiff_rate": 0,
                "ch_swing_rate": 0,
                "ch_whiff_rate": 0,
                "ct_swing_rate": 0,
                "ct_whiff_rate": 0
            }
        },
        "left": {
            "counters": {
                "num_pitches": 0,
                "FB": 0,
                "CB": 0,
                "SL": 0,
                "SM": 0,
                "CH": 0,
                "CT": 0
            },
            "swing_whiff": {
                "swing_rate": 0,
                "whiff_rate": 0,
                "fb_swing_rate": 0,
                "fb_whiff_rate": 0,
                "cb_swing_rate": 0,
                "cb_whiff_rate": 0,
                "sl_swing_rate": 0,
                "sl_whiff_rate": 0,
                "sm_swing_rate": 0,
                "sm_whiff_rate": 0,
                "ch_swing_rate": 0,
                "ch_whiff_rate": 0,
                "ct_swing_rate": 0,
                "ct_whiff_rate": 0
            }
        },
        "right": {
            "counters": {
                "num_pitches": 0,
                "FB": 0,
                "CB": 0,
                "SL": 0,
                "SM": 0,
                "CH": 0,
                "CT": 0
            },
            "swing_whiff": {
                "swing_rate": 0,
                "whiff_rate": 0,
                "fb_swing_rate": 0,
                "fb_whiff_rate": 0,
                "cb_swing_rate": 0,
                "cb_whiff_rate": 0,
                "sl_swing_rate": 0,
                "sl_whiff_rate": 0,
                "sm_swing_rate": 0,
                "sm_whiff_rate": 0,
                "ch_swing_rate": 0,
                "ch_whiff_rate": 0,
                "ct_swing_rate": 0,
                "ct_whiff_rate": 0
            }
        },
    }

    for pitch in zone:

        # pull out commonly used variables for faster recall
        p_type = pitch.pitch_type
        p_res = pitch.pitch_result
        p_hand = "left" if pitch.get_pitcher().throws == "L" else "right"

        # increment total for pitch type
        stats["all"]["counters"][PitchType(pitch.pitch_type).name] += 1
        stats[p_hand]["counters"][PitchType(pitch.pitch_type).name] += 1
        stats[p_hand]["counters"]["num_pitches"] += 1

        # Swing whiff stats by pitch
        if (p_type is 1) and (p_res in ["SS", "IP", "F"]):
            stats["all"]["swing_whiff"]["fb_swing_rate"] += 1
            stats[p_hand]["swing_whiff"]["fb_swing_rate"] += 1
            if p_res in ["SS"]:
                stats["all"]["swing_whiff"]["fb_whiff_rate"] += 1
                stats[p_hand]["swing_whiff"]["fb_whiff_rate"] += 1
        elif (p_type is 2) and (p_res in ["SS", "IP", "F"]):
            stats["all"]["swing_whiff"]["cb_swing_rate"] += 1
            stats[p_hand]["swing_whiff"]["cb_swing_rate"] += 1
            if p_res in ["SS"]:
                stats["all"]["swing_whiff"]["cb_whiff_rate"] += 1
                stats[p_hand]["swing_whiff"]["cb_whiff_rate"] += 1
        elif (p_type is 3) and (p_res in ["SS", "IP", "F"]):
            stats["all"]["swing_whiff"]["sl_swing_rate"] += 1
            stats[p_hand]["swing_whiff"]["sl_swing_rate"] += 1
            if p_res in ["SS"]:
                stats["all"]["swing_whiff"]["sl_whiff_rate"] += 1
                stats[p_hand]["swing_whiff"]["sl_whiff_rate"] += 1
        elif (p_type is 4) and (p_res in ["SS", "IP", "F"]):
            stats["all"]["swing_whiff"]["ch_swing_rate"] += 1
            stats[p_hand]["swing_whiff"]["ch_swing_rate"] += 1
            if p_res in ["SS"]:
                stats["all"]["swing_whiff"]["ch_whiff_rate"] += 1
                stats[p_hand]["swing_whiff"]["ch_whiff_rate"] += 1
        elif (p_type is 5) and (p_res in ["SS", "IP", "F"]):
            stats["all"]["swing_whiff"]["ct_swing_rate"] += 1
            stats[p_hand]["swing_whiff"]["ct_swing_rate"] += 1
            if p_res in ["SS"]:
                stats["all"]["swing_whiff"]["ct_whiff_rate"] += 1
                stats[p_hand]["swing_whiff"]["ct_whiff_rate"] += 1
        elif (p_type is 7) and (p_res in ["SS", "IP", "F"]):
            stats["all"]["swing_whiff"]["sm_swing_rate"] += 1
            stats[p_hand]["swing_whiff"]["sm_swing_rate"] += 1
            if p_res in ["SS"]:
                stats["all"]["swing_whiff"]["sm_whiff_rate"] += 1
                stats[p_hand]["swing_whiff"]["sm_whiff_rate"] += 1

        # Swing whiff stats totals
        if p_res in ["SS", "IP", "F"]:
            stats["all"]["swing_whiff"]["swing_rate"] += 1
            stats[p_hand]["swing_whiff"]["swing_rate"] += 1
            if p_res in ["SS"]:
                stats["all"]["swing_whiff"]["whiff_rate"] += 1
                stats[p_hand]["swing_whiff"]["whiff_rate"] += 1

    # Calculation of summaries from earlier
    for identifier in stats.keys():
        stats[identifier]["swing_whiff"]["whiff_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["whiff_rate"], stats[identifier]["swing_whiff"]["swing_rate"])))
        stats[identifier]["swing_whiff"]["swing_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["swing_rate"], stats[identifier]["counters"]["num_pitches"])))

    for identifier in stats.keys():
        stats[identifier]["swing_whiff"]["fb_whiff_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["fb_whiff_rate"], stats[identifier]["swing_whiff"]["fb_swing_rate"])))
        stats[identifier]["swing_whiff"]["fb_swing_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["fb_swing_rate"], stats[identifier]["counters"]["FB"])))

    for identifier in stats.keys():
        stats[identifier]["swing_whiff"]["cb_whiff_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["cb_whiff_rate"], stats[identifier]["swing_whiff"]["cb_swing_rate"])))
        stats[identifier]["swing_whiff"]["cb_swing_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["cb_swing_rate"], stats[identifier]["counters"]["CB"])))

    for identifier in stats.keys():
        stats[identifier]["swing_whiff"]["sl_whiff_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["sl_whiff_rate"], stats[identifier]["swing_whiff"]["sl_swing_rate"])))
        stats[identifier]["swing_whiff"]["sl_swing_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["sl_swing_rate"], stats[identifier]["counters"]["SL"])))

    for identifier in stats.keys():
        stats[identifier]["swing_whiff"]["ch_whiff_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["ch_whiff_rate"], stats[identifier]["swing_whiff"]["ch_swing_rate"])))
        stats[identifier]["swing_whiff"]["ch_swing_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["ch_swing_rate"], stats[identifier]["counters"]["CH"])))

    for identifier in stats.keys():
        stats[identifier]["swing_whiff"]["ct_whiff_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["ct_whiff_rate"], stats[identifier]["swing_whiff"]["ct_swing_rate"])))
        stats[identifier]["swing_whiff"]["ct_swing_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["ct_swing_rate"], stats[identifier]["counters"]["CT"])))

    for identifier in stats.keys():
        stats[identifier]["swing_whiff"]["sm_whiff_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["sm_whiff_rate"], stats[identifier]["swing_whiff"]["sm_swing_rate"])))
        stats[identifier]["swing_whiff"]["sm_swing_rate"] = percentage(truncate(zero_division_handler(
            stats[identifier]["swing_whiff"]["sm_swing_rate"], stats[identifier]["counters"]["SM"])))

    return stats
