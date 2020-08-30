# All stats functions pertaining to games pages
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
