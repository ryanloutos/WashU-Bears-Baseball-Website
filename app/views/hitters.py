from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.forms import NewOutingFromCSV, SeasonForm, OpponentForm, BatterForm
from app.forms import OutingPitchForm, NewOutingFromCSVPitches, EditUserForm
from app.forms import ChangePasswordForm, EditBatterForm, EditOpponentForm
from app.forms import NewBatterForm
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat, Game
from app.stats import calcPitchPercentages, pitchUsageByCount, calcAverageVelo
from app.stats import calcPitchStrikePercentage, calcPitchWhiffRate
from app.stats import createPitchPercentagePieChart, velocityOverTimeLineChart
from app.stats import pitchStrikePercentageBarChart, avgPitchVeloPitcher
from app.stats import pitchUsageByCountLineCharts, pitchStrikePercentageSeason
from app.stats import pitchUsageSeason, seasonStatLine, staffBasicStats
from app.stats import staffPitchStrikePercentage
from app.stats import outingPitchStatistics, outingTimeToPlate, veloOverTime
from app.stats import stats_opponent_scouting_stats, stats_opponent_batters_stat_lines


hitters = Blueprint("hitters", __name__)

# ***************-HITTERS HOMEPAGE-*************** #
@hitters.route('/hitters/home', methods=['GET', 'POST'])
@login_required
def hitters_home():
    '''
    HITTERS HOMEPAGE:

    RETURN:
        -opponent.html which displays the homepage/info page
            for that opponent
    '''
    # get the Opponent object assicated with the id
    opponent = Opponent.query.filter_by(id=1).first()

    # bug or user trying to view opponent that DNE
    if not opponent:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template('hitters/hitters_home.html',
                           title=opponent,
                           opponent=opponent)


@hitters.route("/hitters/games", methods=["GET", "POST"])
@login_required
def hitters_games():

    opponent = Opponent.query.filter_by(id=1).first()
    if not opponent:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    seasons = []
    for game in opponent.games:
        season = game.get_season()
        if season not in seasons:
            seasons.append(season)

    return render_template(
        '/hitters/hitters_games.html',
        title=opponent,
        opponent=opponent,
        seasons=seasons
    )


@hitters.route("/hitters/stats", methods=["GET", "POST"])
@login_required
def hitters_stats():

    opponent = Opponent.query.filter_by(id=1).first()
    if not opponent:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    batters_stat_line, batters_hard_hit, pitch_usage_count, swing_whiff_rate = stats_opponent_batters_stat_lines(opponent)

    return render_template(
        '/hiters/hitters_stats.html',
        title=opponent,
        opponent=opponent,
        pitch_usage_count=pitch_usage_count,
        swing_whiff_rate=swing_whiff_rate,
        batters_stat_line=batters_stat_line,
        batters_hard_hit=batters_hard_hit
    )


@hitters.route("/hitters/inactive_roster")
@login_required
def hitters_inactive_roster():

    # get opponent object
    opponent = Opponent.query.filter_by(id=1).first()

    # either bug or admin trying to edit opponent that doesn't exist
    if not opponent:
        flash('URL does not exist')
        return redirect(url_for('main.index'))    # get opponent object

    return render_template(
        "hitters/hitters_inactive_roster.html",
        opponent=opponent
    )


@hitters.route('/hitters/edit', methods=['GET', 'POST'])
@login_required
def hitters_edit():

    # if user is not an admin, they can't create a new opponent
    if not current_user.admin:
        flash('You are not an admin and cannot edit an opponent')
        return redirect(url_for('main.index'))

    # get opponent object
    opponent = Opponent.query.filter_by(id=1).first()

    # either bug or admin trying to edit opponent that doesn't exist
    if not opponent:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    # once 'create opponent' button is pressed
    form = EditOpponentForm()
    if form.validate_on_submit():

        file_name = opponent.id
        file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                "..",
                                "static",
                                "images",
                                "team_logos",
                                f"{file_name}.png")

        form.file.data.save(file_loc)

        # get the updated Opponent name and commit to database
        opponent.name = form.name.data
        db.session.commit()

        # redirect back to opponent page
        flash('Congratulations, you just edited Hitters!')
        return redirect(url_for('hitters.hitters_home'))

    return render_template('hitters/hitters_edit.html',
                           title='Edit Hitters',
                           opponent=opponent,
                           form=form)
