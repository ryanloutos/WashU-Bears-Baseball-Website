from flask import Blueprint, jsonify, request
from flask_login import login_required
from app import db
from app.stats import batterSwingWhiffRatebyPitchbyCount, teamImportantStatsSeason, staffBasicStats
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat, Pitcher
from datetime import datetime

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
    req_data = request.get_json()

    if req_data is None:
        return jsonify({
            "status": "failure",
            "error": "Request not processable as JSON."
        })

    pitches = req_data["pitches"]
    outing_info = req_data["outing"]

    # set season variable
    season = None
    seasons = Season.query.all()
    for s in seasons:
        name = f"{s.semester} {s.year}"
        if name == outing_info["season"]:
            season = s

    # set opponent variable
    opponent = Opponent.query.filter_by(name=outing_info["opponent"]).first()

    # set up date object
    date = datetime.strptime(outing_info["date"], "%Y-%m-%d")

    # create outing object
    outing = Outing(
        date=date,
        opponent_id=opponent.id,
        season_id=season.id,
        pitcher_id=outing_info["pitcher"]
    )

    # add outing to db
    db.session.add(outing)
    db.session.commit()
    
    new_at_bat = True
    current_at_bat = None
    balls = 0
    strikes = 0
    count = f'{balls}-{strikes}'
    for index, pitch in enumerate(pitches):

        batter_id = pitch["batter_id"]

        if new_at_bat:
            at_bat = AtBat(
                batter_id=batter_id,
                outing_id=outing.id
            )
            db.session.add(at_bat)
            db.session.commit()
            current_at_bat = at_bat
            new_at_bat = False
        
        pitch_num = index + 1

        hit_spot = pitch["hit_spot"]
        if hit_spot == '0':
            hit_spot = False
        if hit_spot == '1':
            hit_spot = True

        time_to_plate = pitch["time_to_plate"]
        if time_to_plate == "":
            time_to_plate = None

        loc_x = pitch["loc_x"]
        if loc_x in ["", "null", None]:
            loc_x = None

        loc_y = pitch["loc_y"]
        if loc_y in ["", "null", None]:
            loc_y = None
        
        spray_x = pitch["spray_x"]
        if spray_x in ["", "null", None]:
            spray_x = None

        spray_y = pitch["spray_y"]
        if spray_y in ["", "null", None]:
            spray_y = None
        

        pitch = Pitch(
            atbat_id=current_at_bat.id,
            pitch_num=pitch_num,
            batter_id=batter_id,
            velocity=pitch["velocity"],
            lead_runner=pitch["lead_runner"],
            time_to_plate=time_to_plate,
            pitch_type=pitch["pitch_type"],
            pitch_result=pitch["pitch_result"],
            hit_spot=hit_spot,
            count=count,
            ab_result=pitch["ab_result"],
            traj=pitch["traj"],
            fielder=pitch["fielder"],
            inning=pitch["inning"],
            loc_x=loc_x,
            loc_y=loc_y,
            spray_x=spray_x,
            spray_y=spray_y
        )

        balls, strikes, count = updateCount(
            balls,
            strikes,
            pitch.pitch_result,
            pitch.ab_result,
            season
        )

        # print(pitch.atbat_id)
        # print(pitch.pitch_num)
        # print(pitch.batter_id)
        # print(pitch.velocity)
        # print(pitch.lead_runner)
        # print(pitch.time_to_plate)
        # print(pitch.pitch_type)
        # print(pitch.pitch_result)
        # print(pitch.hit_spot)
        # print(pitch.count)
        # print(pitch.ab_result)
        # print(pitch.traj)
        # print(pitch.fielder)
        # print(pitch.inning)

        db.session.add(pitch)
        db.session.commit()

        if pitch.ab_result is not '':
            new_at_bat = True


    return_data = {
        "status": "success",
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