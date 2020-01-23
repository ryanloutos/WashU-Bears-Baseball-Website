from flask import Blueprint, jsonify, request, send_file, url_for, send_from_directory
from flask_login import login_required
from app.stats import batterSwingWhiffRatebyPitchbyCount, teamImportantStatsSeason, staffBasicStats
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat, Pitcher
import os

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


@api.route("/api/staff/arm_care")
@login_required
def download_arm_care():

    return send_from_directory(
        "static", "files/in_season_arm_care.pdf",
        as_attachment=True,
        mimetype="application/pdf",
        attachment_filename="ARM CARE PROGRAM - In-Season - 2020.pdf")
