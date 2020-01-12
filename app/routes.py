from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
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

# ***************-SEASON HOMEPAGE-*************** #
@app.route('/season/<id>')
@login_required
def season(id):
    '''
    SEASON HOMEPAGE:

    PARAM:
        -id: The season id (primary key) of the season
            that is requested to be displayed

    RETURN:
        -season.html which displays all of the outings
            associated with that season
    '''

    # gets the Season object associated with the id parameter
    season = Season.query.filter_by(id=id).first()

    # either bug or user trying to access a season id that DNE
    if not season:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    # outings associated with the specific season
    outings = Outing.query.filter_by(season_id=id).order_by(Outing.date).all()

    return render_template('season/season.html',
                           title=season,
                           outings=outings,
                           season=season)


# ***************-OPPONENT HOMEPAGE-*************** #
@app.route('/opponent/<id>', methods=['GET', 'POST'])
@login_required
def opponent(id):
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


@app.route("/opponent/<id>/GamesResults", methods=["GET", "POST"])
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


@app.route("/opponent/<id>/ScoutingStats", methods=["GET", "POST"])
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
@app.route('/all_opponents', methods=['GET', 'POST'])
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
@app.route('/opponent/<id>/roster', methods=['GET', 'POST'])
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

# ***************-NEW SEASON-*************** #
@app.route('/new_season', methods=['GET', 'POST'])
@login_required
def new_season():
    '''
    NEW SEASON:
    Can create a new season for outings to be associated
    with

    PARAM:
        -None

    RETURN:
        -new_season.html and redirects to index page
            once a new season was successfully created
    '''
    # if user is not an admin, they can't create a new season
    if not current_user.admin:
        flash('You are not an admin and cannot create a season')
        return redirect(url_for('main.index'))

    # when the Create Season button is pressed...
    form = SeasonForm()
    if form.validate_on_submit():

        # insert data from form into season table
        season = Season(semester=form.semester.data,
                        year=form.year.data,
                        current_season=form.current_season.data)

        # send Season object to data table
        db.session.add(season)
        db.session.commit()

        # redirect back to login page
        flash('Congratulations, you just made a new season!')
        return redirect(url_for('main.index'))

    return render_template('season/new_season.html',
                           title='New Season',
                           form=form)

# ***************-EDIT SEASON-*************** #
@app.route('/edit_season/<id>', methods=['GET', 'POST'])
@login_required
def edit_season(id):
    '''
    EDIT SEASON:
    Can edit a current season (like making it the new current
        season)

    PARAM:
        -id: The season id that wants to be edited

    RETURN:
        -edit_season.html and redirects to the season page
            once the season was edited
    '''
    # if user is not an admin, they can't create a new season
    if not current_user.admin:
        flash('You are not an admin and cannot edit a season')
        return redirect(url_for('main.index'))

    # get the season that wants to be edited
    season = Season.query.filter_by(id=id).first()

    # if the season doesn't exist, redirect
    if not season:
        flash("This season doesn't exist")
        return redirect(url_for('main.index'))

    # when the Edit Season button is pressed...
    form = SeasonForm()
    if form.validate_on_submit():

        # if this season become the current season
        if form.current_season.data:
            seasons = Season.query.all()
            for s in seasons:
                s.current_season = False

        # make the changes to the season
        season.semester = form.semester.data
        season.year = form.year.data
        season.current_season = form.current_season.data

        # commit the changes made above
        db.session.commit()

        # redirect to season homepage
        flash('Changes made!')
        return redirect(url_for('season', id=id))

    return render_template('season/edit_season.html',
                           title='New Season',
                           season=season,
                           form=form)

# ***************-NEW OPPONENT-*************** #
@app.route('/new_opponent', methods=['GET', 'POST'])
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
@app.route('/edit_opponent/<id>', methods=['GET', 'POST'])
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
        return redirect(url_for('opponent', id=opponent.id))

    return render_template('opponent/edit_opponent.html',
                           title='Edit Opponent',
                           opponent=opponent,
                           form=form)


@app.context_processor
def template_variables():
    """Acts as the filler for main.html data. This will provide the seasons for the season selector.

    Returns:
        [dict] -- [contians season info for drop downs]
    """
    return dict(
        current_season=getCurrentSeason(),
        old_seasons=getOldSeasons())


@app.context_processor
def utility_functions():
    def truncate(n, decimals=2):
        """Truncates the passed value to decimal places.

        Arguments :
            n {number} -- Number to be truncated

        Keyword Arguments :
            decimals {int} -- Number of decimal places to truncate to(default : {2})

        Returns :
            [int]-- truncated verison of passed value
        """
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier
    return dict(
        truncate=truncate
    )


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
