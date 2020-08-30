# General stats calculation file
import math
import lxml
import pygal

from app import db

from enum import Enum

from app.models import Game
from app.models import Batter
from app.models import Season
from app.models import Outing

from pygal.style import DefaultStyle
from pygal.style import DarkSolarizedStyle

from app.stats.util import truncate
from app.stats.util import PitchType
from app.stats.util import percentage
from app.stats.util import zero_division_handler


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
                pitches_per_count[pitch.count][PitchType(
                    pitch.pitch_type).name] += 1

                if pitch.pitch_result in ["SS", "F", "IP"]:
                    swings_per_count[pitch.count][PitchType(
                        pitch.pitch_type).name] += 1
                    if pitch.pitch_result in ["SS"]:
                        whiffs_per_count[pitch.count][PitchType(
                            pitch.pitch_type).name] += 1

    # calculate batter totals
    for count, val in pitches_per_count.items():
        for pitch, num in val.items():
            # calculate swing rate
            if val[pitch] != 0:
                swing_rate_by_count[count][pitch] = truncate(
                    swings_per_count[count][pitch] / val[pitch])

                # calculate whiff rate
                if swings_per_count[count][pitch] != 0:
                    whiff_rate_by_count[count][pitch] = truncate(
                        whiffs_per_count[count][pitch] / swings_per_count[count][pitch])

    return (swing_rate_by_count, whiff_rate_by_count)


def batterSwingWhiffRatebyPitchbyCount2(batter, seasons=[]):
    """
    second version
    """

    pitches_per_count = {
        "FB": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "SM": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "SL": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "CB": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "CH": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "CT": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "thrown": {"0-0": 0, "0-1": 0, "0-2": 0, "1-0": 0, "1-1": 0, "1-2": 0, "2-0": 0, "2-1": 0, "2-2": 0, "3-0": 0, "3-1": 0, "3-2": 0}
    }

    swing_whiff_rate_new = {
        "FB": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "SM": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "SL": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "CB": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "CH": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "CT": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}}
    }

    pitches_total = 0

    # iterate through all batter at_bats
    for at_bat in batter.at_bats:
        for pitch in at_bat.pitches:
            pitches_per_count[PitchType(
                pitch.pitch_type).name][pitch.count]["usages"] += 1
            pitches_per_count["thrown"][pitch.count] += 1
            pitches_total += 1

            # Swing whiff rate
            swing_whiff_rate_new[PitchType(
                pitch.pitch_type).name][pitch.count]["thrown"] += 1
            if pitch.pitch_result in ["SS", "IP", "F"]:
                # for swing rate calculation
                swing_whiff_rate_new[PitchType(
                    pitch.pitch_type).name][pitch.count]["swings"] += 1

                # for whiff rate calculateion
                if pitch.pitch_result in ["SS"]:
                    swing_whiff_rate_new[PitchType(
                        pitch.pitch_type).name][pitch.count]["whiffs"] += 1

    # Usage rate calc
    for pitch_type, pitch_vals in pitches_per_count.items():
        if pitch_type != "thrown":
            for count, vals in pitch_vals.items():
                if pitches_per_count["thrown"][count] > 0:
                    vals["percent"] = percentage(
                        truncate(vals["usages"] / pitches_per_count["thrown"][count]))

    # SWING/WHIFF rate new calc
    for pitch_type, pitch_vals in swing_whiff_rate_new.items():
        for count, vals in pitch_vals.items():
            if vals["thrown"] > 0:
                # whiff rate calc
                if vals["swings"] > 0:
                    vals["whiffs"] = percentage(
                        truncate(vals["whiffs"] / vals["swings"]))

                # swing rate calc
                vals["swings"] = percentage(
                    truncate(vals["swings"] / vals["thrown"]))

    return (pitches_per_count, swing_whiff_rate_new)


def game_pitching_stats(game, opponent_id):

    stats_by_outing = []
    game_stats = {
        "BF": 0,
        "Pitches": 0,
        "Hits": 0,
        "K": 0,
        "BB": 0,
        "HBP": 0,
        "SP": 0,
        "FPS": 0,
        "FB Avg": 0,
        "2S Avg": 0
    }

    game_strikes = 0
    game_fps = 0
    game_total_fb_velo = 0
    game_total_2s_velo = 0
    game_total_fb_pitches = 0
    game_total_2s_pitches = 0

    for outing in game.outings:
        if outing.pitcher.opponent_id == opponent_id:
            outing_stats = {
                "outing_id": outing.id,
                "Pitcher": outing.pitcher,
                "BF": 0,
                "Pitches": 0,
                "Hits": 0,
                "K": 0,
                "BB": 0,
                "HBP": 0,
                "SP": 0,
                "FPS": 0,
                "FB Avg": 0,
                "2S Avg": 0
            }
            strikes = 0
            fps = 0
            total_fb_velo = 0
            total_2s_velo = 0
            total_fb_pitches = 0
            total_2s_pitches = 0

            for at_bat in outing.at_bats:
                # updated batters faced
                outing_stats["BF"] += 1
                game_stats["BF"] += 1

                # set boolean so fps can be analyzed
                first_pitch = True

                # look at pitches for the at bat
                for pitch in at_bat.pitches:

                    # update total number of pitches
                    outing_stats["Pitches"] += 1
                    game_stats["Pitches"] += 1

                    # update total first pitch strikes
                    if first_pitch:
                        if pitch.pitch_result is not "B":
                            fps += 1
                            game_fps += 1
                        first_pitch = False

                    # update total number of strikes
                    if pitch.pitch_result is not "B":
                        strikes += 1
                        game_strikes += 1

                    # check the ab results and update accordingly
                    if pitch.ab_result in ["1B", "2B", "3B", "HR"]:
                        outing_stats["Hits"] += 1
                        game_stats["Hits"] += 1
                    if pitch.ab_result in ["K", "KL"]:
                        outing_stats["K"] += 1
                        game_stats["K"] += 1
                    if pitch.ab_result == "BB":
                        outing_stats["BB"] += 1
                        game_stats["BB"] += 1
                    if pitch.ab_result == "HBP":
                        outing_stats["HBP"] += 1
                        game_stats["HBP"] += 1

                    # update pitch velo variables to calc averages
                    if pitch.velocity not in [None, ""]:
                        if pitch.pitch_type == 1:
                            total_fb_pitches += 1
                            game_total_fb_pitches += 1
                            total_fb_velo += pitch.velocity
                            game_total_fb_velo += pitch.velocity
                        if pitch.pitch_type == 7:
                            total_2s_pitches += 1
                            game_total_2s_pitches += 1
                            total_2s_velo += pitch.velocity
                            game_total_2s_velo += pitch.velocity

            # divide by zero check and calc velo averages
            if total_fb_pitches == 0:
                outing_stats["FB Avg"] = 0
            else:
                outing_stats["FB Avg"] = truncate(
                    total_fb_velo/total_fb_pitches, 1)

            if total_2s_pitches == 0:
                outing_stats["2S Avg"] = 0
            else:
                outing_stats["2S Avg"] = truncate(
                    total_2s_velo/total_2s_pitches, 1)

            # calc FPS and Strike percentages
            if outing_stats["BF"] > 0:
                outing_stats["FPS"] = percentage(fps/outing_stats["BF"])
            if outing_stats["Pitches"] > 0:
                outing_stats["SP"] = percentage(
                    strikes/outing_stats["Pitches"])

            # append to return array
            stats_by_outing.append(outing_stats)

    # divide by zero check and calc velo averages
    if game_total_fb_pitches == 0:
        game_stats["FB Avg"] = 0
    else:
        game_stats["FB Avg"] = truncate(
            game_total_fb_velo/game_total_fb_pitches, 1)

    if game_total_2s_pitches == 0:
        game_stats["2S Avg"] = 0
    else:
        game_stats["2S Avg"] = truncate(
            game_total_2s_velo/game_total_2s_pitches, 1)

    # calc FPS and Strike percentages
    if game_stats["BF"] > 0:
        game_stats["FPS"] = percentage(game_fps/game_stats["BF"])
    if game_stats["Pitches"] > 0:
        game_stats["SP"] = percentage(game_strikes/game_stats["Pitches"])

    return stats_by_outing, game_stats


def game_hitting_stats(game, opponent_id):

    batters = {}

    for outing in game.outings:
        if outing.opponent_id == opponent_id:
            for at_bat in outing.at_bats:

                # get batter object associated with at bat
                batter = Batter.query.filter_by(id=at_bat.batter_id).first()

                # Check to see if batter has appeared already
                if batter not in batters.keys():
                    batters[batter] = {
                        "AB": 1,       # at bats
                        "pitches": 0,  # pitches
                        "hits": 0,     # hits
                        "ks": 0,       # strikeouts
                        "bbs": 0,      # walks
                        "swr": 0,      # swing rate
                        "wfr": 0       # Whiff rate
                    }
                else:  # add an at bat to existing batter
                    batters[batter]["AB"] += 1

                # iterate through pitches to get individual stat categories
                for pitch in at_bat.pitches:

                    # add pitch to this batter's count
                    batters[batter]["pitches"] += 1

                    # if there was a result to the AB process it correctly
                    if pitch.ab_result not in [None, ""]:

                        # processing for hits
                        if pitch.ab_result in ["1B", "2B", "3B", "HR"]:
                            batters[batter]["hits"] += 1

                        # processing for strikeouts
                        if pitch.ab_result in ["K", "KL", "D3->Out", "D3->Safe"]:
                            batters[batter]["ks"] += 1

                        # processing for walks and HBP
                        if pitch.ab_result in ["BB", "HBP"]:
                            batters[batter]["bbs"] += 1

                    # individual pitch processing
                    if pitch.pitch_result in ["SS", "F", "IP"]:
                        batters[batter]["swr"] += 1

                        # if they swung and missed the pitch
                        if pitch.pitch_result in ["SS"]:
                            batters[batter]["wfr"] += 1

    # run calculations for swing rate and whiff rate
    for stats in batters.values():

        # calculate whiff rate
        if stats["swr"] != 0:
            stats["wfr"] = percentage(truncate(stats["wfr"] / stats["swr"]))

        # calculate swing rate
        if stats["pitches"] != 0:
            stats["swr"] = percentage(
                truncate(stats["swr"] / stats["pitches"]))

    return batters


def batter_summary_game_stats(game, batter):

    # stat trackers
    at_bats = 0
    pitches_seen = 0

    for outing in game.outings:
        for at_bat in outing.at_bats:
            if at_bat.batter_id == batter.id:

                # add to ad_bats
                at_bats += 1

                # add pitches to counter
                for pitch in at_bat.pitches:
                    pitches_seen += 1

    return (at_bats, pitches_seen)


def stats_opponent_scouting_stats(opponent):
    """DEPRECIATED. THIS FUNCTION WAS COMBINED INTO stats_opponent_batters_stat_lines SO THAT LOAD
    TIMES WOULD BE REDUCED BY PROCESSING PITCHES FEWER TIMES.

    Designed to be the holder which calculates all stats to be displayed on the oppoent
    scouting/stats page. Combined so loop processing must only occur once.

    Arguments:
        opponent {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    pitches_per_count = {
        "FB": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "SM": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "SL": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "CB": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "CH": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "CT": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "thrown": {"0-0": 0, "0-1": 0, "0-2": 0, "1-0": 0, "1-1": 0, "1-2": 0, "2-0": 0, "2-1": 0, "2-2": 0, "3-0": 0, "3-1": 0, "3-2": 0}
    }

    swing_whiff_rate_new = {
        "FB": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "SM": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "SL": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "CB": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "CH": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "CT": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}}
    }

    pitches_total = 0

    for game in opponent.games:
        for outing in game.outings:
            for at_bat in outing.at_bats:
                for pitch in at_bat.pitches:

                    # USAGE AND USAGE PERCENTAGE
                    # add a pitch to a counts pitch type and total pitches and pitches in a count
                    pitches_per_count[PitchType(
                        pitch.pitch_type).name][pitch.count]["usages"] += 1
                    pitches_per_count["thrown"][pitch.count] += 1
                    pitches_total += 1

                    # SWING WHIFF RATE
                    swing_whiff_rate_new[PitchType(
                        pitch.pitch_type).name][pitch.count]["thrown"] += 1
                    if pitch.pitch_result in ["SS", "IP", "F"]:
                        # for swing rate calculation
                        swing_whiff_rate_new[PitchType(
                            pitch.pitch_type).name][pitch.count]["swings"] += 1

                        # for whiff rate calculateion
                        if pitch.pitch_result in ["SS"]:
                            swing_whiff_rate_new[PitchType(
                                pitch.pitch_type).name][pitch.count]["whiffs"] += 1

    # print(swing_whiff_rate_new)

    # Usage rate calc
    for pitch_type, pitch_vals in pitches_per_count.items():
        if pitch_type != "thrown":
            for count, vals in pitch_vals.items():
                if pitches_per_count["thrown"][count] > 0:
                    vals["percent"] = percentage(
                        truncate(vals["usages"] / pitches_per_count["thrown"][count]))

    # SWING/WHIFF rate new calc
    for pitch_type, pitch_vals in swing_whiff_rate_new.items():
        for count, vals in pitch_vals.items():
            if vals["thrown"] > 0:
                # whiff rate calc
                if vals["swings"] > 0:
                    vals["whiffs"] = percentage(
                        truncate(vals["whiffs"] / vals["swings"]))

                # swing rate calc
                vals["swings"] = percentage(
                    truncate(vals["swings"] / vals["thrown"]))

    return (pitches_per_count, swing_whiff_rate_new)


def stats_opponent_batters_stat_lines(opponent):
    """Designed to handle stat calculations for opponent scouting/stats page. This function calculates a team's
    active member's collective swing and whiff rates, our career pitch usage vs their active hitters, their active member's
    career and current season stat_line vs out staff, their active member's current and career hard hit ball percentage

    Arguments:
        opponent {opponent object} -- opponent team to be analyzed

    Returns:
        [tuple] -- a number of very complicated data arrays and dictionary containing values to be placed in web-pages
    """
    # Swing and whiff rate variables
    pitches_per_count = {
        "FB": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "SM": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "SL": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "CB": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "CH": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "CT": {"0-0": {"usages": 0, "percent": 0}, "0-1": {"usages": 0, "percent": 0}, "0-2": {"usages": 0, "percent": 0}, "1-0": {"usages": 0, "percent": 0}, "1-1": {"usages": 0, "percent": 0}, "1-2": {"usages": 0, "percent": 0}, "2-0": {"usages": 0, "percent": 0}, "2-1": {"usages": 0, "percent": 0}, "2-2": {"usages": 0, "percent": 0}, "3-0": {"usages": 0, "percent": 0}, "3-1": {"usages": 0, "percent": 0}, "3-2": {"usages": 0, "percent": 0}},
        "thrown": {"0-0": 0, "0-1": 0, "0-2": 0, "1-0": 0, "1-1": 0, "1-2": 0, "2-0": 0, "2-1": 0, "2-2": 0, "3-0": 0, "3-1": 0, "3-2": 0}
    }
    swing_whiff_rate_new = {
        "FB": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "SM": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "SL": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "CB": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "CH": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}},
        "CT": {"0-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "0-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "1-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "2-2": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-0": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-1": {"swings": 0, "whiffs": 0, "thrown": 0}, "3-2": {"swings": 0, "whiffs": 0, "thrown": 0}}
    }
    pitches_total = 0

    # Stat line variables
    batter_stat_line = []

    # hard hit variables
    batter_hard_hit_line = []

    for batter in opponent.batters:
        if batter.retired in [0, "0"]:

            temp_stat_line = {
                "name": batter.name_and_number(),
                "class": batter.grad_year,
                "ab": 0,
                "h": 0,
                "1b": 0,
                "2b": 0,
                "3b": 0,
                "hr": 0,
                "bb": 0,
                "k": 0,
                "current_ab": 0,
                "current_h": 0,
                "current_1b": 0,
                "current_2b": 0,
                "current_3b": 0,
                "current_hr": 0,
                "current_bb": 0,
                "current_k": 0
            }
            temp_hard_hit = {
                "name": batter.name_and_number(),
                "num_hard": 0,
                "num_total": 0,
                "percent": 0,
                "current_num_hard": 0,
                "current_num_total": 0,
                "current_percent": 0
            }

            for at_bat in batter.at_bats:
                temp_stat_line["ab"] += 1
                if at_bat.get_season().current_season:
                    temp_stat_line["current_ab"] += 1
                for pitch in at_bat.pitches:

                    # if there was an ab_result, do calc for stat line and hard_hit
                    if pitch.ab_result not in [None, ""]:

                        # hit stats
                        if pitch.ab_result in ["1b", "1B"]:
                            temp_stat_line["h"] += 1
                            temp_stat_line["1b"] += 1
                        elif pitch.ab_result in ["2b", "2B"]:
                            temp_stat_line["h"] += 1
                            temp_stat_line["2b"] += 1
                        elif pitch.ab_result in ["3b", "3B"]:
                            temp_stat_line["h"] += 1
                            temp_stat_line["3b"] += 1
                        elif pitch.ab_result in ["HR", "hr"]:
                            temp_stat_line["h"] += 1
                            temp_stat_line["hr"] += 1
                        elif pitch.ab_result in ["bb", "BB", "hbp", "HBP"]:
                            temp_stat_line["bb"] += 1
                        elif pitch.ab_result in ["k", "kl", "K", "KL"]:
                            temp_stat_line["k"] += 1

                        # current season hit stats
                        if at_bat.get_season().current_season:
                            if pitch.ab_result in ["1b", "1B"]:
                                temp_stat_line["current_h"] += 1
                                temp_stat_line["current_1b"] += 1
                            elif pitch.ab_result in ["2b", "2B"]:
                                temp_stat_line["current_h"] += 1
                                temp_stat_line["current_2b"] += 1
                            elif pitch.ab_result in ["3b", "3B"]:
                                temp_stat_line["current_h"] += 1
                                temp_stat_line["current_3b"] += 1
                            elif pitch.ab_result in ["HR", "hr"]:
                                temp_stat_line["current_h"] += 1
                                temp_stat_line["current_hr"] += 1
                            elif pitch.ab_result in ["bb", "BB", "hbp", "HBP"]:
                                temp_stat_line["current_bb"] += 1
                            elif pitch.ab_result in ["k", "kl", "K", "KL"]:
                                temp_stat_line["current_k"] += 1

                        # Hard hit stats
                        if pitch.ab_result in ["IP->Out", "1B", "2B", "3B", "HR", "Error", "FC"]:
                            temp_hard_hit["num_total"] += 1
                            if pitch.hit_hard == 1:
                                temp_hard_hit["num_hard"] += 1

                            # current season hard hit stats
                            if at_bat.get_season().current_season:
                                temp_hard_hit["current_num_total"] += 1
                                if pitch.hit_hard == 1:
                                    temp_hard_hit["current_num_hard"] += 1

                    # USAGE AND USAGE PERCENTAGE
                    # add a pitch to a counts pitch type and total pitches and pitches in a count
                    pitches_per_count[PitchType(
                        pitch.pitch_type).name][pitch.count]["usages"] += 1
                    pitches_per_count["thrown"][pitch.count] += 1
                    pitches_total += 1

                    # SWING WHIFF RATE
                    swing_whiff_rate_new[PitchType(
                        pitch.pitch_type).name][pitch.count]["thrown"] += 1
                    if pitch.pitch_result in ["SS", "IP", "F"]:
                        # for swing rate calculation
                        swing_whiff_rate_new[PitchType(
                            pitch.pitch_type).name][pitch.count]["swings"] += 1

                        # for whiff rate calculateion
                        if pitch.pitch_result in ["SS"]:
                            swing_whiff_rate_new[PitchType(
                                pitch.pitch_type).name][pitch.count]["whiffs"] += 1

            # hard hit calcs
            if temp_hard_hit["num_total"] > 0:
                temp_hard_hit["percent"] = percentage(
                    truncate(temp_hard_hit["num_hard"] / temp_hard_hit["num_total"]))
            if temp_hard_hit["current_num_total"] > 0:
                temp_hard_hit["current_percent"] = percentage(truncate(
                    temp_hard_hit["current_num_hard"] / temp_hard_hit["current_num_total"]))

            # append stat line and hard hit to storage array
            batter_stat_line.append(temp_stat_line)
            batter_hard_hit_line.append(temp_hard_hit)

    # USAGE RATE CALC
    for pitch_type, pitch_vals in pitches_per_count.items():
        if pitch_type != "thrown":
            for count, vals in pitch_vals.items():
                if pitches_per_count["thrown"][count] > 0:
                    vals["percent"] = percentage(
                        truncate(vals["usages"] / pitches_per_count["thrown"][count]))

    # SWING/WHIFF rate new calc
    for pitch_type, pitch_vals in swing_whiff_rate_new.items():
        for count, vals in pitch_vals.items():
            if vals["thrown"] > 0:
                # whiff rate calc
                if vals["swings"] > 0:
                    vals["whiffs"] = percentage(
                        truncate(vals["whiffs"] / vals["swings"]))

                # swing rate calc
                vals["swings"] = percentage(
                    truncate(vals["swings"] / vals["thrown"]))

    return (batter_stat_line, batter_hard_hit_line, pitches_per_count, swing_whiff_rate_new)


def batter_ball_in_play_stats(batter):
    ball_in_play = {"h": 0, "1b": 0, "2b": 0,
                    "3b": 0, "hr": 0, "bb": 0, "k": 0}
    hard_hit = {"num_hard": 0, "num_total": 0, "percent": 0}

    ball_in_play_games = {
        "career": {},
        "current": {}
    }
    hard_hit_games = {
        "career": {},
        "current": {}
    }
    # Each game for batter has blank stat line to start
    for game in batter.get_games():
        if game not in [None, ""]:
            ball_in_play_games["career"][game] = {
                "h": 0, "1b": 0, "2b": 0, "3b": 0, "hr": 0, "bb": 0, "k": 0}
            hard_hit_games["career"][game] = {
                "num_hard": 0, "num_total": 0, "percent": 0}
            if game.get_season().current_season:
                ball_in_play_games["current"][game] = {
                    "h": 0, "1b": 0, "2b": 0, "3b": 0, "hr": 0, "bb": 0, "k": 0}
                hard_hit_games["current"][game] = {
                    "num_hard": 0, "num_total": 0, "percent": 0}

    # iterate through batter ab's for values
    for at_bat in batter.at_bats:
        game = at_bat.get_game()
        if game not in [None, ""]:
            for pitch in at_bat.pitches:

                # Ball in play stats
                if pitch.ab_result not in [None, ""]:
                    game = at_bat.get_game()

                    # career ball in play stats
                    if pitch.ab_result in ["1b", "1B"]:
                        ball_in_play_games["career"][game]["h"] += 1
                        ball_in_play_games["career"][game]["1b"] += 1
                    elif pitch.ab_result in ["2b", "2B"]:
                        ball_in_play_games["career"][game]["h"] += 1
                        ball_in_play_games["career"][game]["2b"] += 1
                    elif pitch.ab_result in ["3b", "3B"]:
                        ball_in_play_games["career"][game]["h"] += 1
                        ball_in_play_games["career"][game]["3b"] += 1
                    elif pitch.ab_result in ["HR", "hr"]:
                        ball_in_play_games["career"][game]["h"] += 1
                        ball_in_play_games["career"][game]["hr"] += 1
                    elif pitch.ab_result in ["bb", "BB", "hbp", "HBP"]:
                        ball_in_play_games["career"][game]["bb"] += 1
                    elif pitch.ab_result in ["k", "kl", "K", "KL"]:
                        ball_in_play_games["career"][game]["k"] += 1

                    # current season ball in play stats
                    if at_bat.get_season().current_season:
                        if pitch.ab_result in ["1b", "1B"]:
                            ball_in_play_games["current"][game]["h"] += 1
                            ball_in_play_games["current"][game]["1b"] += 1
                        elif pitch.ab_result in ["2b", "2B"]:
                            ball_in_play_games["current"][game]["h"] += 1
                            ball_in_play_games["current"][game]["2b"] += 1
                        elif pitch.ab_result in ["3b", "3B"]:
                            ball_in_play_games["current"][game]["h"] += 1
                            ball_in_play_games["current"][game]["3b"] += 1
                        elif pitch.ab_result in ["HR", "hr"]:
                            ball_in_play_games["current"][game]["h"] += 1
                            ball_in_play_games["current"][game]["hr"] += 1
                        elif pitch.ab_result in ["bb", "BB", "hbp", "HBP"]:
                            ball_in_play_games["current"][game]["bb"] += 1
                        elif pitch.ab_result in ["k", "kl", "K", "KL"]:
                            ball_in_play_games["current"][game]["k"] += 1

                # Hard hit stats
                if pitch.ab_result in ["IP->Out", "1B", "2B", "3B", "HR", "Error", "FC"]:

                    # career hard hit stats
                    hard_hit_games["career"][game]["num_total"] += 1
                    if pitch.hit_hard:
                        hard_hit_games["career"][game]["num_hard"] += 1

                    # current season hard hit stats
                    if at_bat.get_season().current_season:
                        hard_hit_games["current"][game]["num_total"] += 1
                        if pitch.hit_hard:
                            hard_hit_games["current"][game]["num_hard"] += 1

    # calculations for hard hit
    for game in batter.get_games():
        if game not in [None, ""] and hard_hit_games["career"][game]["num_total"] > 0:

            # career hard hit
            hard_hit_games["career"][game]["percent"] = percentage(
                truncate(
                    hard_hit_games["career"][game]["num_hard"] / hard_hit_games["career"][game]["num_total"]))

            # current season hard hit
            if game.get_season().current_season:
                hard_hit_games["current"][game]["percent"] = percentage(
                    truncate(
                        hard_hit_games["current"][game]["num_hard"] / hard_hit_games["current"][game]["num_total"]))

    return (ball_in_play_games, hard_hit_games)
