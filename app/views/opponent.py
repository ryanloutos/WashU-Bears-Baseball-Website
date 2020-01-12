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
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat
from app.stats import calcPitchPercentages, pitchUsageByCount, calcAverageVelo
from app.stats import calcPitchStrikePercentage, calcPitchWhiffRate
from app.stats import createPitchPercentagePieChart, velocityOverTimeLineChart
from app.stats import pitchStrikePercentageBarChart, avgPitchVeloPitcher
from app.stats import pitchUsageByCountLineCharts, pitchStrikePercentageSeason
from app.stats import pitchUsageSeason, seasonStatLine, staffBasicStats
from app.stats import staffPitcherAvgVelo, staffPitchStrikePercentage
from app.stats import outingPitchStatistics, outingTimeToPlate, veloOverTime
from app.stats import teamImportantStatsSeason

# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random


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

    file_loc = os.path.join("images",
                            "team_logos",
                            f"{opponent.id}.png")

    # bug or user trying to view opponent that DNE
    if not opponent:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template('opponent/opponent_home.html',
                           title=opponent,
                           opponent=opponent,
                           file_loc=file_loc)


@opponent.route("/opponent/<id>/GamesResults", methods=["GET", "POST"])
@login_required
def opponent_games_results(id):

    opponent = Opponent.query.filter_by(id=id).first()
    if not opponent:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    return render_template(
        '/opponent/opponent_GamesResults.html',
        title=opponent,
        opponent=opponent
    )


@opponent.route("/opponent/<id>/ScoutingStats", methods=["GET", "POST"])
@login_required
def opponent_scouting_stats(id):
    opponent = Opponent.query.filter_by(id=id).first()
    if not opponent:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    return render_template(
        '/opponent/opponent_ScoutingStats.html',
        title=opponent,
        opponent=opponent
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
    opponents = Opponent.query.all()
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
    '''
    NEW OPPONENT:
    Can create a new opponent for outings to be associated
    with

    PARAM:
        -None

    RETURN:
        -new_opponent.html and redirects to index page
            once a new opponent was successfully created
    '''
    # if user is not an admin, they can't create a new opponent
    if not current_user.admin:
        flash('You are not an admin and cannot create a opponent')
        return redirect(url_for('main.index'))

    # when the Create Opponent button is pressed...
    form = OpponentForm()
    if form.validate_on_submit():

        # create Opponent object from form data
        opponent = Opponent(name=form.name.data)

        # send Opponent object to database
        db.session.add(opponent)
        db.session.commit()

        # create the batter objects from the form and send to database
        for subform in form.batter:

            # create Batter object
            batter = Batter(name=subform.fullname.data,
                            short_name=subform.nickname.data,
                            bats=subform.bats.data,
                            grad_year=subform.grad_year.data,
                            opponent_id=opponent.id)

            # add before commit
            db.session.add(batter)

        # commit the batters to database
        db.session.commit()

        # redirect back to login page
        flash('Congratulations, you just made a new opponent!')
        return redirect(url_for('main.index'))

    return render_template('opponent/new_opponent.html',
                           title='New Opponent',
                           form=form)


# ***************-EDIT OPPONENT-*************** #
@opponent.route('/edit_opponent/<id>', methods=['GET', 'POST'])
@login_required
def edit_opponent(id):
    '''
    EDIT OPPONENT:
    Can edit an opponent for outings to be associated
    with

    PARAM:
        -id: The outing id (primary key) that wants to be
            edited

    RETURN:
        -edit_opponent.html and redirects to opponent page
            once an opponent was successfully edited
    '''

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


# ***************-HELPFUL FUNCTIONS-*************** #
def getAvailablePitchers():
    '''
    Gets all of the string names you are allowed to create outings for

    PARAM:
        -None

    RETURN:
        - [array] -- [strings of pitchers names]
    '''

    # gets all the User objects that are players on the team
    pitchers_objects = User.query.filter(User.grad_year != 'Coach/Manager').all()

    # set the available choices that someone can create an outing for
    available_pitchers = []

    if current_user.admin:
        for p in pitchers_objects:
            available_pitchers.append((p.username, p))

    return available_pitchers


def getAvailableBatters(outing_id):
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first_or_404()

    batters_tuples = []
    for batter in opponent.batters:
        batters_tuples.append((batter.id, batter))

    return batters_tuples


def validate_CSV(file_loc):
    '''
    Validates an uploaded outing csv file to see if we can create pitches
    from it.

    PARAM:
        -file_loc {string} -- string location of the file to be validated

    RETURN:
        [boolean] -- boolean for if the file is determined valid
    '''

    # fields required to construct a pitch from Pitch class in modals. We need
    # to check if all of these exist.
    pitch_attributes = [
        "velocity", "lead_runner", "time_to_plate", "pitch_type",
        "pitch_result", "hit_spot", "ab_result", "traj", "fielder",
        "inning"]
    with open(file_loc) as f:

        csv_file = csv.DictReader(f)
        invalid_pitch_found = False  # State var to see if pitches are valid

        for pitch_num, row in enumerate(csv_file):
            keys = row.keys()

            # Check if the our necessary keys is contained within the csv
            # keys provided.
            if set(pitch_attributes).issubset(set(keys)):
                print("You have the necessary keys")

            else:
                invalid_pitch_found = True

                # Debug statement. Eventually move to user facing so they can
                # adjust input.
                for attr in pitch_attributes:
                    if attr not in keys:
                        print("Pitch num " + pitch_num + " missing: " + attr)
                break

        if invalid_pitch_found:
            return False
        else:
            return True


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


def getCurrentSeason():
    current_season = Season.query.filter_by(current_season=True).first()
    return current_season


def getOldSeasons():
    old_seasons = Season.query.filter_by(current_season=False).order_by(Season.year).all()
    return old_seasons
