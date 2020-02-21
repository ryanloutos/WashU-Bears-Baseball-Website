from flask import Blueprint
from flask import render_template
from flask_login import login_required
from app import db

from app.models import User, Outing, Pitch, Season, Pitcher
from app.stats import staffBasicStats
from app.stats import staffAdvancedStats
from app.stats import teamImportantStatsSeason

# setup blueprint
staff = Blueprint('staff', __name__)

# ***************-STAFF HOMEPAGE-*************** # 
@staff.route("/staff", methods=["GET", "POST"])
@login_required
def staff_home():
    '''
    Homepage: shows the roster and staff goals
    '''
    pitchers = Pitcher.query.filter(Pitcher.retired != 1).filter(Pitcher.opponent_id == 1).order_by(Pitcher.name).all()
    return render_template(
        "staff/home/staff_home.html",
        title="Bears Pitching",
        pitchers=pitchers
    )


# ***************-STAFF ARMCARE-*************** # 
@staff.route("/staff/armcare", methods=["GET", "POST"])
@login_required
def staff_armcare():
    '''
    Armcare: shows the current arm care program for the team
    '''
    return render_template(
        "staff/staff_armcare.html",
        title="Arm Care",
    )


# ***************-STAFF BASIC STATS-*********** #
# @staff.route('/staff/basic_stats', methods=['GET', 'POST'])
# @login_required
# def staff_basic_stats():
#     """Basic stats of all players on current roster.

#     Arguments:
#         -None

#     Returns:
#         staff_basic_stats.html -- list of basic stats for all players
#         currently on roster
#     """
#     pitchers = Pitcher.query.filter(Pitcher.retired != 1).filter(Pitcher.opponent_id == 1).order_by(Pitcher.name).all()    
#     seasons = Season.query.order_by(Season.year).all()

#     staff_stat_summary, players_stat_summary = staffBasicStats(pitchers)

#     return render_template(
#         'staff/staff_basic_stats.html',
#         staff_stat_summary=staff_stat_summary,
#         players_stat_summary=players_stat_summary,
#         seasons=seasons)


# # ***************-STAFF ADVANCED STATS-*********** #
@staff.route('/staff/advanced_stats', methods=['GET', 'POST'])
@login_required
def staff_advanced_stats():
    pitchers = Pitcher.query.filter(Pitcher.retired != 1).filter(Pitcher.opponent_id == 1).order_by(Pitcher.name).all()    

    players, total_velo_averages, total_pct_averages, total_fps_pct, total_whiffs_pct, total_swing_and_miss_pct = staffAdvancedStats(pitchers)

    return render_template(
        'staff/staff_advanced_stats.html',
        players = players,
        total_velo_averages = total_velo_averages,
        total_pct_averages = total_pct_averages,
        total_fps_pct = total_fps_pct,
        total_whiffs_pct = total_whiffs_pct,
        total_swing_and_miss_pct = total_swing_and_miss_pct
    )


# ***************-STAFF RETIRED-*************** # DONE
@staff.route('/staff/retired', methods=['GET', 'POST'])
@login_required
def staff_retired():
    '''
    STAFF RETIRED:
    Pitchers no longer on the team

    PARAM:
        -None

    RETURN:
        -staff_retired.html which displays a table of
            the retired staff
    '''

    retired_pitchers = Pitcher.query.filter(Pitcher.retired == 1).filter(Pitcher.opponent_id == 1).order_by(Pitcher.grad_year).all()

    return render_template('staff/staff_retired.html',
                           title='Retired Pitchers',
                           retired_pitchers=retired_pitchers)
