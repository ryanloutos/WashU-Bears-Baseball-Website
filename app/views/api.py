from flask import Blueprint, jsonify, request, send_file, url_for, send_from_directory
from flask_login import login_required
from app import db
from app.stats import batterSwingWhiffRatebyPitchbyCount, teamImportantStatsSeason, staffBasicStats
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat, Pitcher, Game, Video
from datetime import datetime
import os
import re

api = Blueprint("api", __name__)


@api.route("/api/batter/stats/WhiffRateByCount", methods=["POST"])
@login_required
def batter_stats_whiffrate():
    # get json object from request
    req_data = request.get_json()

    if req_data is None:
        return jsonify({
            "status": "failure",
            "error": "Request not processable as JSON."
        })

    # check to see if parameter we want is provided
    if "seasons" in req_data and "batter_id" in req_data:

        seasons = req_data["seasons"]
        # check to see that seasons from request is a list
        if type(seasons) is not list:
            return jsonify({
                "status": "failure",
                "error": "Data type of seasons is not list"
            })

        batter_id = req_data["batter_id"]
        batter = Batter.query.filter_by(id=batter_id).first()

        # if batter object is not valid, return error statement
        if not batter:
            return jsonify({"status": "failure", "error": "Invalid batter id given"})

        # call to stat calculation
        swing_rate_by_count, whiff_rate_by_count = batterSwingWhiffRatebyPitchbyCount(batter, seasons=seasons)

        # prepare return json
        return_value = {
            "status": "success",
            "data": {
                "swing_rate_by_count": swing_rate_by_count,
                "whiff_rate_by_count": whiff_rate_by_count
            }
        }

        return jsonify(return_value)

    # if required request parameters were not given
    else:
        return jsonify({
            "status": "failure",
            "error": "Required parameters not given in request."
        })


@api.route("/api/staff/stats/importantstats", methods=["POST"])
@login_required
def staff_home_importantstats():
    # req_data = request.get_json()

    # if req_data is None:
    #     return jsonify({
    #         "status": "failure",
    #         "error": "Request not processable as JSON."
    #     })

    pitchers = Pitcher.query.all()

    strike_percentage, fps_percentage, k_to_bb = teamImportantStatsSeason(pitchers)

    return_data = {
        "status": "success",
        "data": {
            "strike_percentage": strike_percentage,
            "fps_percentage": fps_percentage,
            "k_to_bb": k_to_bb
        }
    }
    return jsonify(return_data)


@api.route("/api/staff/stats/basicstats", methods=["POST"])
@login_required
def staff_basic_stats():
    req_data = request.get_json()

    if req_data is None:
        return jsonify({
            "status": "failure",
            "error": "Request not processable as JSON"
        })

    if "seasons" not in req_data:
        return jsonify({
            "status": "failure",
            "error": "Request does not contain necessary info"
        })

    seasons = req_data["seasons"]

    if type(seasons) is not list:
        return jsonify({
            "status": "failure",
            "error": "Seasons request data not in list form"
        })

    pitchers = Pitcher.query.filter(Pitcher.retired != 1).all()

    staff_stat_summary, players_stat_summary = staffBasicStats(pitchers, seasons=seasons)

    return jsonify({
        "data": {
            "staff_stat_summary": staff_stat_summary,
            "player_stat_summary": players_stat_summary
        },
        "status": "success"
    })


@api.route("/api/pitch_tracker", methods=["POST"])
@login_required
def pitch_tracker():
    # get the data send from js
    req_data = request.get_json()

    # if data wasn't sent
    if req_data is None:
        return jsonify({
            "status": "failure",
            "error": "Request not processable as JSON."
        })

    # get info associated with pitch
    pitch_data = req_data["pitch"]
    outing_id = req_data["outing"]
    count = req_data["count"]
    at_bat = req_data["at_bat"]
    pitch_num = req_data["pitch_num"]

    # get the outing object
    outing = Outing.query.filter_by(id=outing_id).first()

    # set the batter_id
    batter_id = pitch_data["batter_id"]

    # if it is the first pitch of the at bat
    if at_bat is "":
        at_bat_object = AtBat(
            batter_id=batter_id,
            outing_id=outing.id
        )
        db.session.add(at_bat_object)
        db.session.commit()
        at_bat = at_bat_object.id

    # cleaning up data
    hit_spot = pitch_data["hit_spot"]
    if hit_spot == '0':
        hit_spot = False
    if hit_spot == '1':
        hit_spot = True

    hit_hard = pitch_data["hit_hard"]
    if hit_hard == '0':
        hit_hard = False
    if hit_hard == '1':
        hit_hard = True

    roll_through = pitch_data["roll_through"]
    if roll_through == '0':
        roll_through = False
    if roll_through == '1':
        roll_through = True

    short_set = pitch_data["short_set"]
    if short_set == '0':
        short_set = False
    if short_set == '1':
        short_set = True

    time_to_plate = pitch_data["time_to_plate"]
    if time_to_plate == "":
        time_to_plate = None

    loc_x = pitch_data["loc_x"]
    print(loc_x)
    if loc_x in ["", "null", None]:
        loc_x = None
    print(loc_x)

    loc_y = pitch_data["loc_y"]
    if loc_y in ["", "null", None]:
        loc_y = None

    spray_x = pitch_data["spray_x"]
    if spray_x in ["", "null", None, 0]:
        spray_x = None

    spray_y = pitch_data["spray_y"]
    if spray_y in ["", "null", None, 0]:
        spray_y = None

    # make a Pitch object
    pitch = Pitch(
        atbat_id=at_bat,
        pitch_num=pitch_num,
        batter_id=batter_id,
        velocity=pitch_data["velocity"],
        lead_runner=pitch_data["lead_runner"],
        time_to_plate=time_to_plate,
        pitch_type=pitch_data["pitch_type"],
        roll_through=roll_through,
        short_set=short_set,
        pitch_result=pitch_data["pitch_result"],
        hit_spot=hit_spot,
        count=count,
        ab_result=pitch_data["ab_result"],
        traj=pitch_data["traj"],
        fielder=pitch_data["fielder"],
        hit_hard=hit_hard,
        inning=pitch_data["inning"],
        loc_x=loc_x,
        loc_y=loc_y,
        spray_x=spray_x,
        spray_y=spray_y,
        notes=pitch_data["notes"]
    )

    # send pitch to database
    db.session.add(pitch)
    db.session.commit()

    # get the balls and strikes from the count
    count_split = pitch.count.split("-")
    balls = int(count_split[0])
    strikes = int(count_split[1])

    # update the count based on result of pitch
    if pitch.pitch_result == "B":
        balls += 1
    elif pitch.pitch_result == "F" and strikes == 2:
        strikes = 2
    else:
        strikes += 1

    # reset count and at bat variable if at bat over
    if (pitch.ab_result != ""):
        balls = 1
        strikes = 1
        at_bat = ""

    # send back data
    return_data = {
        "status": "success",
        "atBat": at_bat,
        "balls": balls,
        "strikes": strikes
    }
    return jsonify(return_data)


def updateCount(balls, strikes, pitch_result, ab_result, season):
    if ab_result is not '':
        if (season.semester == 'Fall'):
            balls = 1
            strikes = 1
        else:
            balls = 0
            strikes = 0
    else:
        if pitch_result is 'B':
            balls += 1
        else:
            if strikes is not 2:
                strikes += 1
    count = f'{balls}-{strikes}'
    return (balls, strikes, count)


@api.route("/api/staff/arm_care")
@login_required
def download_arm_care():

    return send_from_directory(
        "static", "files/in_season_arm_care.pdf",
        as_attachment=True,
        mimetype="application/pdf",
        attachment_filename="ARM CARE PROGRAM - In-Season - 2020.pdf")


@api.route("/api/season/<season_id>/games")
@login_required
def games_in_season(season_id):

    season = Season.query.filter_by(id=season_id).first()
    if not season:
        return jsonify({
            "status": "failure",
            "error": "Season id provided is invalid"
        })

    games = Game.query.filter_by(season_id=season.id).order_by(Game.date).all()

    # put games into jsonable format
    games_ret = []
    for game in games:
        games_ret.append({
            "id": game.id,
            "label": game.__repr__()
        })

    return jsonify({
        "status": "success",
        "games": games_ret
    })


@api.route("/api/outings/season/<season_id>/pitcher/<pitcher_id>")
@login_required
def outings_in_season(season_id, pitcher_id):
    season = Season.query.filter_by(id=season_id).first()
    pitcher = Pitcher.query.filter_by(id=pitcher_id).first()
    if not season:
        return jsonify({
            "status": "failure",
            "error": "Season id provided is invalid"
        })
    if not pitcher:
        return jsonify({
            "status": "failure",
            "error": "Pitcher id provided is invalid"
        })

    outings = Outing.query.filter_by(season_id=season.id).filter_by(pitcher_id=pitcher.id).order_by(Outing.date).all()

    outings_ret = []
    for outing in outings:
        outings_ret.append({
            "id": outing.id,
            "label": outing.__repr__()
        })

    return jsonify({
        "status": "success",
        "outings": outings_ret
    })


@api.route("/api/videos/season/<season_id>/pitcher/<pitcher_id>")
@login_required
def videos_in_season_pitcher(season_id, pitcher_id):
    season = Season.query.filter_by(id=season_id).first()
    pitcher = Pitcher.query.filter_by(id=pitcher_id).first()
    if not season:
        return jsonify({
            "status": "failure",
            "error": "Season id provided is invalid"
        })
    if not pitcher:
        return jsonify({
            "status": "failure",
            "error": "Pitcher id provided is invalid"
        })

    videos = Video.query.filter_by(season_id=season.id).filter_by(pitcher_id=pitcher.id).order_by(Video.date).all()

    video_ids = []
    video_names = []

    for v in videos:
        regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
        match = regex.match(v.link)
        if not match:
            video_ids.append("")
        else:
            video_ids.append(match.group("id"))

        video_names.append(v.__repr__())

    return jsonify({
        "status": "success",
        "video_names": video_names,
        "video_ids": video_ids
    })


@api.route("/api/videos/season/<season_id>/batter/<batter_id>")
@login_required
def videos_in_season_batter(season_id, batter_id):
    season = Season.query.filter_by(id=season_id).first()
    batter = Batter.query.filter_by(id=batter_id).first()
    if not season:
        return jsonify({
            "status": "failure",
            "error": "Season id provided is invalid"
        })
    if not batter:
        return jsonify({
            "status": "failure",
            "error": "Batter id provided is invalid"
        })

    videos = Video.query.filter_by(season_id=season.id).filter_by(batter_id=batter.id).order_by(Video.date).all()

    video_ids = []
    video_names = []

    for v in videos:
        regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
        match = regex.match(v.link)
        if not match:
            video_ids.append("")
        else:
            video_ids.append(match.group("id"))

        video_names.append(v.__repr__())

    return jsonify({
        "status": "success",
        "video_names": video_names,
        "video_ids": video_ids
    })
