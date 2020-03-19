from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.forms import NewOutingFromCSV, NewOpponentForm
from app.forms import OutingPitchForm, NewOutingFromCSVPitches, EditUserForm
from app.forms import ChangePasswordForm, EditBatterForm, EditOpponentForm
from app.forms import NewBatterForm
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat, Game, Pitcher
from app.stats import calcPitchPercentages, pitchUsageByCount, calcAverageVelo
from app.stats import calcPitchStrikePercentage, calcPitchWhiffRate
from app.stats import createPitchPercentagePieChart, velocityOverTimeLineChart
from app.stats import pitchStrikePercentageBarChart, avgPitchVeloPitcher
from app.stats import pitchUsageByCountLineCharts, pitchStrikePercentageSeason
from app.stats import pitchUsageSeason, seasonStatLine, staffBasicStats
from app.stats import staffPitchStrikePercentage
from app.stats import outingPitchStatistics, outingTimeToPlate, veloOverTime
from app.stats import stats_opponent_scouting_stats, stats_opponent_batters_stat_lines

# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random

import re


opponent = Blueprint("opponent", __name__)


# ***************-OPPONENT HOMEPAGE-*************** #
@opponent.route('/opponent/<id>', methods=['GET', 'POST'])
@login_required
def opponent_home(id):
    '''
    OPPONENT HOMEPAGE:

    PARAM:
        -id: The opponent id (primary key) for the opponent
            that the user is trying to view

    RETURN:
        -opponent.html which displays the homepage/info page
            for that opponent
    '''
    # get the Opponent object assicated with the id
    opponent = Opponent.query.filter_by(id=id).first()

    # bug or user trying to view opponent that DNE
    if not opponent:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template('opponent/opponent_home.html',
                           title=opponent,
                           opponent=opponent)


@opponent.route("/opponent/<id>/GamesResults", methods=["GET", "POST"])
@login_required
def opponent_games_results(id):

    opponent = Opponent.query.filter_by(id=id).first()
    if not opponent:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    seasons = []
    for game in opponent.games:
        season = game.get_season()
        if season not in seasons:
            seasons.append(season)

    return render_template(
        '/opponent/opponent_GamesResults.html',
        title=opponent,
        opponent=opponent,
        seasons=seasons
    )


@opponent.route("/opponent/<opponent_id>/ScoutingStats", methods=["GET", "POST"])
@login_required
def opponent_scouting_stats(opponent_id):

    opponent = Opponent.query.filter_by(id=opponent_id).first()
    if not opponent:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    batters_stat_line, batters_hard_hit, pitch_usage_count, swing_whiff_rate = stats_opponent_batters_stat_lines(opponent)

    return render_template(
        '/opponent/opponent_ScoutingStats.html',
        title=opponent,
        opponent=opponent,
        pitch_usage_count=pitch_usage_count,
        swing_whiff_rate=swing_whiff_rate,
        batters_stat_line=batters_stat_line,
        batters_hard_hit=batters_hard_hit
    )


# ***************-ALL OPPONENTS-*************** #
@opponent.route('/all_opponents', methods=['GET', 'POST'])
@login_required
def all_opponents():
    '''
    ALL OPPONENTS HOMEPAGE:

    PARAM:
        -noe

    RETURN:
        -all_opponents.html which displays the a list of all
            the teams opponents
    '''
    # get the Opponent object assicated with the id
    opponents = Opponent.query.order_by(Opponent.name).all()
    if not opponents:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    return render_template('opponent/all_opponents.html',
                           title="All Opponents",
                           opponents=opponents)

# ***************-OPPONENT ROSTER-*************** #
@opponent.route('/opponent/<id>/roster', methods=['GET', 'POST'])
@login_required
def opponent_roster(id):
    '''
    OPPONENT ROSTER:

    PARAM:
        -id: The opponent id (primary key) for the opponent
            that the user is trying to view

    RETURN:
        -opponent.html which displays the homepage/info page
            for that opponent
    '''
    # get the Opponent object assicated with the id
    opponent = Opponent.query.filter_by(id=id).first()

    # bug or user trying to view opponent that DNE
    if not opponent:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template('opponent/opponent_roster.html',
                           title=opponent,
                           opponent=opponent)


# ***************-NEW OPPONENT-*************** #
@opponent.route('/new_opponent', methods=['GET', 'POST'])
@login_required
def new_opponent():
    # if user is not an admin, they can't create a new opponent
    if not current_user.admin:
        flash('You are not an admin and cannot create a opponent')
        return redirect(url_for('main.index'))

    form = NewOpponentForm()
    if form.validate_on_submit():

        opponent = Opponent(name=form.name.data)

        db.session.add(opponent)
        db.session.commit()

        file_name = opponent.id
        file_loc = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "static",
            "images",
            "team_logos",
            f"{file_name}.png"
        )
        form.logo.data.save(file_loc)

        for subform in form.batters:
            if (subform.firstname.data not in ["", None] and
                subform.lastname.data not in ["", None] and
                subform.number.data not in ["", None]):

                initials = getInitialsFromNames(subform.firstname.data, subform.lastname.data)

                batter = Batter(
                    opponent_id=opponent.id,
                    firstname=subform.firstname.data,
                    lastname=subform.lastname.data,
                    number=subform.number.data,
                    initials=initials,
                    bats=subform.bats.data,
                    grad_year=subform.grad_year.data,
                    notes=subform.notes.data,
                    retired=subform.retired.data)
                db.session.add(batter)

        for subform in form.pitchers:
            if (subform.firstname.data not in ["", None] and
                subform.lastname.data not in ["", None] and
                subform.number.data not in ["", None]):

                pitcher = Pitcher(
                    opponent_id=opponent.id,
                    firstname=subform.firstname.data,
                    lastname=subform.lastname.data,
                    number=subform.number.data,
                    throws=subform.throws.data,
                    grad_year=subform.grad_year.data,
                    notes=subform.notes.data,
                    retired=subform.retired.data)
                db.session.add(pitcher)

        db.session.commit()

        flash('Congratulations, you just made a new opponent!')
        return redirect(url_for('main.index'))

    return render_template('opponent/new_opponent.html',
                           title='New Opponent',
                           form=form)

def getInitialsFromNames(firstname, lastname):
    first_initial = re.findall("^\w", firstname)
    last_initial = re.findall("^\w", lastname)
    return f"{first_initial[0]}{last_initial[0]}"

# ***************-EDIT OPPONENT-*************** #
@opponent.route('/edit_opponent/<id>', methods=['GET', 'POST'])
@login_required
def edit_opponent(id):
    # if user is not an admin, they can't create a new opponent
    if not current_user.admin:
        flash('You are not an admin and cannot edit an opponent')
        return redirect(url_for('main.index'))

    # get opponent object
    opponent = Opponent.query.filter_by(id=id).first()

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
        flash('Congratulations, you just edited the opponent!')
        return redirect(url_for('opponent.opponent_home', id=opponent.id))

    return render_template('opponent/edit_opponent.html',
                           title='Edit Opponent',
                           opponent=opponent,
                           form=form)


@opponent.route("/opponent/<id>/inactive_roster")
@login_required
def opponent_inactive_hitters(id):

    # get opponent object
    opponent = Opponent.query.filter_by(id=id).first()

    # either bug or admin trying to edit opponent that doesn't exist
    if not opponent:
        flash('URL does not exist')
        return redirect(url_for('main.index'))    # get opponent object

    return render_template(
        "opponent/opponent_inactive_roster.html",
        opponent=opponent
    )

