from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
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

batter = Blueprint('batter', __name__)

# ***************-BATTER HOMEPAGE-*************** #
@batter.route('/batter/<id>', methods=['GET', 'POST'])
@login_required
def batter_home(id):
    '''
    BATTER HOMEPAGE:

    PARAM:
        -id: The batter id (primary key) for the batter
            that the user is trying to view

    RETURN:
        -batter.html which displays the homepage/info page
            for that batter
    '''

    # get the Batter object associated with the id passed in
    batter = Batter.query.filter_by(id=id).first()

    # either bug or user trying to view a batter that DNE
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template('opponent/batter/batter.html',
                           title=batter.name,
                           batter=batter)


@batter.route("/batter/<batter_id>/at_bats", methods=['GET', 'POST'])
@login_required
def batter_at_bats(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()

    # either bug or user trying to view a batter that DNE
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        '/opponent/batter/batter_at_bats.html',
        batter=batter
    )


@batter.route("/batter/<batter_id>/at_bat/<ab_num>", methods=['GET', 'POST'])
@login_required
def batter_at_bat(batter_id, ab_num):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    at_bat = AtBat.query.filter_by(id=ab_num).first()
    if not at_bat:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    pitcher = at_bat.get_pitcher()

    return render_template(
        '/opponent/batter/batter_at_bat.html',
        at_bat=at_bat,
        pitcher=pitcher,
        batter=batter,
        title=batter.name
    )


@batter.route("/batter/<batter_id>/pitches_against", methods=['GET', 'POST'])
@login_required
def batter_pitches_against(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        'opponent/batter/batter_pitches_against.html',
        title=batter,
        batter=batter
    )


@batter.route("/batter/<batter_id>/spray_chart", methods=['GET', 'POST'])
@login_required
def batter_spray_chart(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        'opponent/batter/batter_spray_chart.html',
        title=batter,
        batter=batter
    )


@batter.route("/batter/<batter_id>/sequencing", methods=['GET', 'POST'])
@login_required
def batter_sequencing(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        'opponent/batter/batter_sequencing.html',
        title=batter,
        batter=batter
    )

# ***************-DELETE BATTER-*************** #
@batter.route('/delete_batter/<id>', methods=['GET', 'POST'])
@login_required
def delete_batter(id):
    '''
    DELETE BATTER
    Can delete an existing batter through this function

    PARAM:
        -id: the batter id (primary key) in which the user
            wants to delete

    RETURN:
        -deletes the batter and redirects to opponent page which the outing
            was associated with
    '''
    # only admins can go back and edit outing data
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('main.index'))

    # get the batter object associated with the id
    batter = Batter.query.filter_by(id=id).first()

    # bug of trying to delete batter that doesn't exist
    if not batter:
        flash("Can't delete a batter that doesn't exist")
        return redirect(url_for('main.index'))

    # delete the batter from database
    db.session.delete(batter)
    db.session.commit()

    return redirect(url_for('opponent.opponent_home', id=batter.opponent_id))

# ***************-EDIT BATTER-*************** #
@batter.route('/edit_batter/<id>', methods=['GET', 'POST'])
@login_required
def edit_batter(id):
    '''
    EDIT BATTER:
    Can edit an already existing batter

    PARAM:
        -id: The batter id (primary key) that wants to be
            edited

    RETURN:
        -edit_batter.html and redirects to opponent page
            once an opponent was successfully edited
    '''
    # make sure user is admin
    if not current_user.admin:
        flash("You are not an admin")
        return redirect(url_for('main.index'))

    # get the correct form
    form = EditBatterForm()

    # get the batter object
    batter = Batter.query.filter_by(id=id).first()

    # bug or trying to edit batter that doesn't exist
    if not batter:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    # set the opponent choices correctly
    opponent_choices = []
    opponents = Opponent.query.all()
    for o in opponents:
        opponent_choices.append((str(o.id), o.name))
    form.opponent.choices = opponent_choices

    # submit is clicked
    if form.validate_on_submit():

        # update info with data from form
        batter.name = form.fullname.data
        batter.short_name = form.nickname.data
        batter.bats = form.bats.data
        batter.grad_year = form.grad_year.data
        batter.retired = form.retired.data

        # commit the changes
        db.session.commit()

        flash('Batter has been adjusted')
        return redirect(url_for('opponent.opponent_roster', id=batter.opponent_id))

    return render_template('opponent/batter/edit_batter.html',
                           title='Edit Batter',
                           batter=batter,
                           form=form)

# ***************-NEW BATTER-*************** #
@batter.route('/new_batter', methods=['GET', 'POST'])
@login_required
def new_batter():
    '''
    NEW BATTER:
    Can create a new batter for a specific opponent

    PARAM:
        -None

    RETURN:
        -new_batter.html
    '''
    # if user is not an admin, they can't create a new season
    if not current_user.admin:
        flash('You are not an admin and cannot create a season')
        return redirect(url_for('main.index'))

    # get the correct form
    form = NewBatterForm()

    # set the opponent choices correctly
    opponent_choices = []
    opponents = Opponent.query.all()
    for o in opponents:
        opponent_choices.append((str(o.id), o.name))
    form.opponent.choices = opponent_choices

    # when the Create Season button is pressed...
    if form.validate_on_submit():

        # insert data from form into season table
        batter = Batter(name=form.fullname.data,
                        short_name=form.nickname.data,
                        bats=form.bats.data,
                        grad_year=form.grad_year.data,
                        opponent_id=form.opponent.data)

        # send Season object to data table
        db.session.add(batter)
        db.session.commit()

        # redirect back to login page
        flash('Congratulations, you just made a new batter!')
        return redirect(url_for('opponent.opponent_home', id=batter.opponent_id))

    return render_template('opponent/batter/new_batter.html',
                           title='New Batter',
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
