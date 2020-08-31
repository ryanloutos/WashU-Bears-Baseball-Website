from flask import Blueprint
from flask import render_template
from flask_login import login_required
from app import db

from app.models import User
from app.models import Pitch
from app.models import Outing
from app.models import Season
from app.models import Pitcher

from app.stats.pitching_stats import staffSeasonGoals
from app.stats.pitching_stats import staffSeasonStats

from datetime import date

# setup blueprint
staff = Blueprint('staff', __name__)

# ***************-STAFF HOMEPAGE-*************** #
@staff.route("/staff", methods=["GET", "POST"])
@login_required
def staff_home():
    pitchers = Pitcher.query.filter(Pitcher.retired != 1).filter(Pitcher.opponent_id == 1).order_by(Pitcher.lastname).all()
    return render_template(
        "staff/home/staff_home.html",
        title="Bears Pitching",
        pitchers=pitchers
    )


# ***************-STAFF ARMCARE-*************** #
@staff.route("/staff/armcare", methods=["GET", "POST"])
@login_required
def staff_armcare():
    return render_template (
        "staff/staff_armcare.html",
        title="Arm Care",
    )


# # ***************-STAFF SEASON STATS-*********** #
@staff.route('/staff/season_stats', methods=['GET', 'POST'])
@login_required
def staff_season_stats():
    pitchers = Pitcher.query.filter(Pitcher.retired != 1).filter(Pitcher.opponent_id == 1).order_by(Pitcher.lastname).all()    

    first_date = date(2000, 1, 1)
    second_date = date(9999, 12, 31)
    players, staff = staffSeasonStats(pitchers, first_date, second_date, False)

    return render_template (
        'staff/staff_season_stats.html',
        title = "Staff Season Stats",
        players = players,
        staff = staff
    )


# ***************-STAFF RETIRED-*************** # DONE
@staff.route('/staff/retired', methods=['GET', 'POST'])
@login_required
def staff_retired():

    retired_pitchers = Pitcher.query.filter(Pitcher.retired == 1).filter(Pitcher.opponent_id == 1).order_by(Pitcher.grad_year).all()

    return render_template (
        'staff/staff_retired.html',
        title = 'Retired Pitchers',
        retired_pitchers = retired_pitchers
    )
