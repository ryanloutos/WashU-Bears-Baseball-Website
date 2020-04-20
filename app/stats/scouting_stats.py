import lxml
import math
import pygal

from app import db

from app.models import Game
from app.models import Batter
from app.models import Outing
from app.models import Season

from pygal.style import DefaultStyle
from pygal.style import DarkSolarizedStyle

from app.stats.util import truncate
from app.stats.util import PitchType
from app.stats.util import percentage
from app.stats.util import ZONE_CONSTANTS
from app.stats.util import get_zone_region
from app.stats.util import zero_division_handler


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
    """Helper function for repeated calculations for
    zone_division_stats_batter

    Arguments:
        zone {dict} -- dictionary of pitch objects that correlate
        to a certain region of the strikezone.

    Returns:
        [dict] -- complex dictionary containing statistical breakdowns
        for the pitches in the region passed in.
    """
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
        }
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


def whiff_coords_by_pitch_batter(batter):
    """Returns the x,y coordinates for every pitch that a batter
    swung and missed at

    Arguments:
        batter {Batter object} -- batter to be analyzed

    Returns:
        dictionary -- A dict of array containing swing and miss
        x,y coordinates by pitch for a batter
    """
    stats = {
        "FB": [],
        "CB": [],
        "SL": [],
        "CH": [],
        "CT": [],
        "SM": []
    }

    for at_bat in batter.at_bats:
        for pitch in at_bat.pitches:
            if pitch.loc_y is None or pitch.loc_x is None:
                continue
            if pitch.pitch_result in ['SS']:
                stats[PitchType(pitch.pitch_type).name].append((pitch.loc_x, pitch.loc_y))

    return stats


def whiff_coords_by_pitch_pitcher(pitcher):
    """Returns the x,y coordinates for every pitch that a pitcher
    threw that was whiffed by a hitter

    Arguments:
        pitcher {Pitcher object} -- Pitcher to be analyzed

    Returns:
        dictionary -- A dict of array containing swing and miss
        x,y coordinates by pitch for a pitcher
    """
    stats = {
        "FB": [],
        "CB": [],
        "SL": [],
        "CH": [],
        "CT": [],
        "SM": []
    }

    for outing in pitcher.outings:
        for ab in outing.at_bats:
            for pitch in ab.pitches:
                if pitch.loc_y is None or pitch.loc_x is None:
                    continue
                if pitch.pitch_result in ['SS']:
                    stats[PitchType(pitch.pitch_type).name].append((pitch.loc_x, pitch.loc_y))

    return stats


def pitcher_dynamic_zone_scouting(pitcher):
    """For a given pitcher, generates a dictionary tracking a number
    of statistical categories for different regions of the strikezone.

    Arguments:
        pitcher {pitcher object} -- Pitcher to be analyzed

    Returns:
        [dictionary] -- Complex dictionary containing summary values for
        each category. Calculation needs to happen elsewhere.
    """
    zones_data = {}

    # Setup zones_data stat categories
    for x in range(5):
        for y in range(5):
            zones_data[f"{x}{y}"] = {
                "swing_rate": {},
                "whiff_rate": {},
                "foul_rate": {},
                "in_play_rate": {},
                "in_play_out_rate": {},
                "in_play_safe_rate": {},
                "count": {}
            }
    # setup pitch types for stat category
    for k1, v1 in zones_data.items():
        for k2, v2 in zones_data[k1].items():
            zones_data[k1][k2] = {
                "FB": 0,
                "CB": 0,
                "SL": 0,
                "CH": 0,
                "CT": 0,
                "SM": 0
            }

    # process data
    for outing in pitcher.outings:
        for at_bat in outing.at_bats:
            for pitch in at_bat.pitches:
                # only the pitches we care about
                if pitch.loc_x in ["", None] or pitch.loc_y in ["", None]:
                    continue

                # for faster memory access
                region = get_zone_region(pitch)
                p_type = PitchType(pitch.pitch_type).name
                p_res = pitch.pitch_result

                zones_data[region]["count"][p_type] += 1

                if p_res in ["SS", "F", "IP"]:
                    zones_data[region]["swing_rate"][p_type] += 1
                    if p_res in ["SS"]:
                        zones_data[region]["whiff_rate"][p_type] += 1
                    elif p_res in ["F"]:
                        zones_data[region]["foul_rate"][p_type] += 1
                    else:
                        zones_data[region]["in_play_rate"][p_type] += 1
                        if pitch.ab_result in ["IP->Out", "FC", "Error", "Other"]:
                            zones_data[region]["in_play_out_rate"][p_type] += 1
                        else:
                            zones_data[region]["in_play_safe_rate"][p_type] += 1

    return zones_data


def batter_dynamic_zone_scouting(batter):
    """For a given batter, generates a dictionary tracking a number
    of statistical categories for different regions of the strikezone.

    Arguments:
        batter {batter object} -- Batter to be analyzed

    Returns:
        [dictionary] -- Complex dictionary containing summary values for
        each category. Calculation needs to happen elsewhere.
    """

    zones_data = {}

    # Setup zones_data statistical categories
    for x in range(5):
        for y in range(5):
            zones_data[f"{x}{y}"] = {
                "swing_rate": {},
                "whiff_rate": {},
                "foul_rate": {},
                "in_play_rate": {},
                "in_play_out_rate": {},
                "in_play_safe_rate": {},
                "count": {}
            }
    # Setup pitch types for each category
    for k1, v1 in zones_data.items():
        for k2, v2 in zones_data[k1].items():
            zones_data[k1][k2] = {
                "FB": 0,
                "CB": 0,
                "SL": 0,
                "CH": 0,
                "CT": 0,
                "SM": 0
            }

    # process data
    for at_bat in batter.at_bats:
        for pitch in at_bat.pitches:
            # only the pitches we care about
            if pitch.loc_x in ["", None] or pitch.loc_y in ["", None]:
                continue

            # Pull commonly used vars for faster mem access
            region = get_zone_region(pitch)
            p_type = PitchType(pitch.pitch_type).name
            p_res = pitch.pitch_result

            zones_data[region]["count"][p_type] += 1

            if p_res in ["SS", "F", "IP"]:
                zones_data[region]["swing_rate"][p_type] += 1
                if p_res in ["SS"]:
                    zones_data[region]["whiff_rate"][p_type] += 1
                elif p_res in ["F"]:
                    zones_data[region]["foul_rate"][p_type] += 1
                else:
                    zones_data[region]["in_play_rate"][p_type] += 1
                    if pitch.ab_result in ["IP->Out", "FC", "Error", "Other"]:
                        zones_data[region]["in_play_out_rate"][p_type] += 1
                    else:
                        zones_data[region]["in_play_safe_rate"][p_type] += 1

    return zones_data
