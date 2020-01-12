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

# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random

outing = Blueprint("outing", __name__)

# ***************-OUTING HOMEPAGE-*************** #
@outing.route('/outing/<id>', methods=['GET', 'POST'])
@login_required
def outing_home(id):
    '''
    OUTING HOMEPAGE:

    PARAM:
        -outing_id: The outing id (primary key) of the outing
            that is requested to be displayed

    RETURN:
        -outing_home.html which displays the homepage for
            the outing
    '''
    # get the outing object associated by the id in the url
    outing = Outing.query.filter_by(id=id).first()

    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('main.index'))

    # get opponent associated with outing
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first()

    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('main.index'))

    # render template with all the statistical data calculated from the outing
    return render_template(
        'outing/outing_home.html',
        title=outing,
        outing=outing,
        opponent=opponent)

# ***************-OUTING PBP-*************** #
@outing.route('/outing/<id>/pbp', methods=['GET', 'POST'])
@login_required
def outing_pbp(id):
    '''
    OUTING PITCH BY PITCH:

    PARAM:
        -outing_id: The outing id (primary key) of the outing
            that is requested to be displayed

    RETURN:
        -outing.html which displays all of the pitches and
            at bats from the outing
    '''
    # get the outing object associated by the id in the url
    outing = Outing.query.filter_by(id=id).first()
    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('main.index'))

    opponent = Opponent.query.filter_by(id=outing.opponent_id).first()

    # Get statistical data
    usages, usage_percentages = calcPitchPercentages(outing)
    counts, counts_percentages = pitchUsageByCount(outing)
    pitch_avg_velo = calcAverageVelo(outing)
    pitch_strike_percentage = calcPitchStrikePercentage(outing)
    pitch_whiff = calcPitchWhiffRate(outing)

    # Get statistical graphics
    usage_percentages_pie_chart = createPitchPercentagePieChart(usage_percentages)
    velocity_over_time_line_chart = velocityOverTimeLineChart(outing)
    strike_percentage_bar_chart = pitchStrikePercentageBarChart(pitch_strike_percentage)
    usage_percent_by_count_line_chart = pitchUsageByCountLineCharts(counts_percentages)

    # render template with all the statistical data calculated from the outing
    return render_template(
        'outing/outing_pbp.html',
        title=outing,
        outing=outing,
        opponent=opponent,
        usages=usages,
        usage_percentages=usage_percentages,
        usage_percentages_pie_chart=usage_percentages_pie_chart,
        counts=counts,
        counts_percentages=counts_percentages,
        pitch_avg_velo=pitch_avg_velo,
        pitch_strike_percentage=pitch_strike_percentage,
        pitch_whiff=pitch_whiff,
        velocity_over_time_line_chart=velocity_over_time_line_chart,
        strike_percentage_bar_chart=strike_percentage_bar_chart,
        usage_percent_by_count_line_chart=usage_percent_by_count_line_chart
    )

# ***************-OUTING ADVANCED STATS-*************** #
@outing.route('/outing/<id>/stats/advanced', methods=['GET', 'POST'])
@login_required
def outing_stats_advanced(id):
    '''
    OUTING ADVANCED STATS:

    PARAM:
        -outing_id: The outing id (primary key) of the outing
            that is requested to be displayed

    RETURN:
        -outing.html which displays some advanced statistics
            for a specific outing
    '''
    # get the outing object associated by the id in the url
    outing = Outing.query.filter_by(id=id).first()
    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('main.index'))

    opponent = Opponent.query.filter_by(id=outing.opponent_id).first()

    # Get statistical data
    pitch_stats = outingPitchStatistics(outing)
    time_to_plate = outingTimeToPlate(outing)

    # setting up horizontal axis for line chart
    horizontal_axis = []
    i = 1
    for ab in outing.at_bats:
        for p in ab.pitches:
            horizontal_axis.append(i)
            i += 1

    velos = veloOverTime(outing)

    # render template with all the statistical data calculated from the outing
    return render_template(
        'outing/outing_stats_advanced.html',
        title=outing,
        outing=outing,
        opponent=opponent,
        pitch_stats=pitch_stats,
        time_to_plate=time_to_plate,
        labels=horizontal_axis,
        velos=velos
    )


@outing.route('/outing/<id>/stats/basic', methods=["GET", "POST"])
@login_required
def outing_stats_basic(id):

    outing = Outing.query.filter_by(id=id).first()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        '/outing/outing_stats_basic.html',
        title=outing,
        outing=outing
    )


@outing.route('/outing/<id>/videos', methods=["GET", "POST"])
@login_required
def outing_videos(id):

    outing = Outing.query.filter_by(id=id).first()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        '/outing/outing_videos.html',
        title=outing,
        outing=outing
    )

# ***************-NEW OUTING-*************** #
@outing.route('/new_outing', methods=['GET', 'POST'])
@login_required
def new_outing():
    '''
    NEW OUTING:
    Can create a new outing and pitches associated with
    that outing

    PARAM:
        -None

    RETURN:
        -new_outing.html allows user to enter in info for a
            specific outing and creates the outing object
            along with all the pitches objects associated
            with the outing
    '''
    form = OutingForm()

    # set the choices for all available pitchers
    form.pitcher.choices = getAvailablePitchers()

    # when the 'Create Outing' button is pressed
    if form.validate_on_submit():

        # gets the user associated the username of the pitcher the outing
        # is being created for
        user = User.query.filter_by(username=form.pitcher.data).first_or_404()

        # creates a new outing object based on form data and user
        outing = Outing(date=form.date.data,
                        opponent_id=form.opponent.data.id,
                        season_id=form.season.data.id,
                        user_id=user.id)

        # add the new outing to the database before pitches so pitches have a
        # outing_id associated with them
        db.session.add(outing)
        db.session.commit()

        # redirects back to home page after outing was successfully created
        flash("New Outing Created!")
        return redirect(url_for('new_outing_pitches', outing_id=outing.id))

    return render_template('outing/new_outing.html',
                           title='New Outing',
                           form=form)

# ***************-NEW OUTING PITCHES-*************** #
@outing.route('/new_outing_pitches/<outing_id>', methods=['GET', 'POST'])
@login_required
def new_outing_pitches(outing_id):

    # get the form associated with entering in X number of pitches
    form = OutingPitchForm()

    # set up batter choices
    for subform in form.pitch:
        subform.batter_id.choices = getAvailableBatters(outing_id)

    # get the outing/season associated with the id
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    season = Season.query.filter_by(id=outing.season_id).first_or_404()

    # if "add pitches" button was clicked
    if form.validate_on_submit():

        # sets up count for first pitch of outing
        if (season.semester == 'Fall'):
            balls = 1
            strikes = 1
            count = f'{balls}-{strikes}'
        else:
            balls = 0
            strikes = 0
            count = f'{balls}-{strikes}'

        # Boolean variable to help with adding AtBat objects to the database
        new_at_bat = True

        # variable to hold the current AtBat object
        current_at_bat = None

        # add each individual pitch to the database
        for index, subform in enumerate(form.pitch):

            # get the batter_id for the AtBat and Pitch objects
            batter_id = subform.batter_id.data

            # if a new at bat has started, make a new AtBat object
            if new_at_bat:
                at_bat = AtBat(
                    batter_id=batter_id,
                    outing_id=outing_id)

                # Add the AtBat object to database
                db.session.add(at_bat)
                db.session.commit()

                # Set the current_at_bat for subsequent pitches accordingly
                current_at_bat = at_bat

                # So new at_bat variables aren't made every pitch
                new_at_bat = False

            # sets the pitch_num column automatically
            pitch_num = index + 1

            # create Pitch object
            pitch = Pitch(
                atbat_id=current_at_bat.id,
                pitch_num=pitch_num,
                batter_id=batter_id,
                velocity=subform.velocity.data,
                lead_runner=subform.lead_runner.data,
                time_to_plate=subform.time_to_plate.data,
                pitch_type=subform.pitch_type.data,
                pitch_result=subform.pitch_result.data,
                hit_spot=subform.hit_spot.data,
                count=count,
                ab_result=subform.ab_result.data,
                traj=subform.traj.data,
                fielder=subform.fielder.data,
                inning=subform.inning.data)

            # update count based on current count and pitch result
            balls, strikes, count = updateCount(balls,
                                                strikes,
                                                pitch.pitch_result,
                                                pitch.ab_result,
                                                season)

            # adds pitch to database
            db.session.add(pitch)
            db.session.commit()

            # after the pitch was made, if the at_bat ended, reset variable
            # so a new at_bat starts during the next loop
            if pitch.ab_result is not '':
                new_at_bat = True

        flash('Pitches added to outing!')
        return redirect(url_for('outing', id=outing_id))

    return render_template(
        'outing/new_outing_pitches.html',
        title='New Outing Pitches',
        form=form
    )

# ***************-EDIT OUTING PITCHES-*************** #
@outing.route('/edit_outing_pitches/<outing_id>', methods=['GET', 'POST'])
@login_required
def edit_outing_pitches(outing_id):
    '''
    EDIT OUTING PITCHES
    Can edit pitches of an existing outing

    PARAM:
        -outing_id: the outing id (primary key) in which the user
            wants to access

    RETURN:
        -edit_outing_pitches.html which allows user to edit the pitches of
            the outing requested. The function deletes the existing pitches
            and uploads the updated ones to the database.
    '''

    # get the database objects needed for the function
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    user = User.query.filter_by(id=outing.user_id).first_or_404()
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first_or_404()
    season = Season.query.filter_by(id=outing.season_id).first_or_404()

    # only admins can go back and edit outing data
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('main.index'))

    # get the correct form
    form = OutingPitchForm()

    # set up batter choices here
    for subform in form.pitch:
        subform.batter_id.choices = getAvailableBatters(outing_id)

    # when edit wants to be made
    if form.validate_on_submit():

        # delete all of the pitches/at_bats associated with the outing
        for at_bat in outing.at_bats:
            for p in at_bat.pitches:
                db.session.delete(p)
            db.session.delete(at_bat)

        # commit the changes
        db.session.commit()

        # sets up count for first pitch of outing
        if season.semester == 'Fall':
            balls = 1
            strikes = 1
            count = f'{balls}-{strikes}'
        else:
            balls = 0
            strikes = 0
            count = f'{balls}-{strikes}'

        # Boolean variable to help with adding AtBat objects to the database
        new_at_bat = True

        # variable to hold the current AtBat object
        current_at_bat = None

        # add each individual pitch to the database
        for index, subform in enumerate(form.pitch):

            # get the batter_id for the AtBat and Pitch objects
            batter_id = subform.batter_id.data

            # if a new at bat has started, make a new AtBat object
            if new_at_bat:
                at_bat = AtBat(batter_id=batter_id,
                               outing_id=outing_id)

                # Add the AtBat object to database
                db.session.add(at_bat)
                db.session.commit()

                # Set the current_at_bat for subsequent pitches accordingly
                current_at_bat = at_bat

                # So new at_bat variables aren't made every pitch
                new_at_bat = False

            # sets the pitch_num column automatically
            pitch_num = index + 1

            # create Pitch object
            pitch = Pitch(atbat_id=current_at_bat.id,
                          pitch_num=pitch_num,
                          batter_id=batter_id,
                          velocity=subform.velocity.data,
                          lead_runner=subform.lead_runner.data,
                          time_to_plate=subform.time_to_plate.data,
                          pitch_type=subform.pitch_type.data,
                          pitch_result=subform.pitch_result.data,
                          hit_spot=subform.hit_spot.data,
                          count=count,
                          ab_result=subform.ab_result.data,
                          traj=subform.traj.data,
                          fielder=subform.fielder.data,
                          inning=subform.inning.data)

            # update count based on current count and pitch result
            balls, strikes, count = updateCount(balls,
                                                strikes,
                                                pitch.pitch_result,
                                                pitch.ab_result,
                                                season)

            # adds pitch to database
            db.session.add(pitch)
            db.session.commit()

            # after the pitch was made, if the at_bat ended, reset variable
            # so a new at_bat starts during the next loop
            if pitch.ab_result is not '':
                new_at_bat = True

        # redirect to user page
        flash('The outing has been adjusted!')
        return redirect(url_for('outing', id=outing.id))

    # sets up subforms so they are visible in edit_outing.html
    num_pitches = 0
    for at_bat in outing.at_bats:
        for pitch in at_bat.pitches:
            num_pitches += 1
    for p in range(1, num_pitches):
        form.pitch.append_entry()

    # set up batter choices here
    for subform in form.pitch:
        subform.batter_id.choices = getAvailableBatters(outing_id)

    batters = []
    for b in opponent.batters:
        batters.append(b)

    return render_template('outing/edit_outing_pitches.html',
                           title='Edit Outing',
                           outing=outing,
                           opponent=opponent,
                           form=form)

# ***************-EDIT OUTING-*************** #
@outing.route('/edit_outing/<outing_id>', methods=['GET', 'POST'])
@login_required
def edit_outing(outing_id):

    # get correct form
    form = OutingForm()

    # get the available pitchers to choose from
    form.pitcher.choices = getAvailablePitchers()

    # get objects from database
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first_or_404()
    this_season = Season.query.filter_by(id=outing.season_id).first_or_404()
    all_seasons = Season.query.all()
    this_pitcher = User.query.filter_by(id=outing.user_id).first_or_404()
    all_pitchers = User.query.filter(User.grad_year != 'Coach/Manager').all()

    # only admins can go back and edit outing data
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('main.index'))

    # when edit wants to be made
    if form.validate_on_submit():

        # get the user object from form
        pitcher = User.query.filter_by(username=form.pitcher.data).first_or_404()

        # update data for outing object
        outing.user_id = pitcher.id
        outing.date = form.date.data
        outing.season_id = form.season.data.id

        # commit changes to database
        db.session.commit()

        # redirect to user page
        flash('The outing has been adjusted!')
        return redirect(url_for('pitcher.pitcher_home', id=pitcher.id))

    return render_template('outing/edit_outing.html',
                           title='Edit Outing',
                           outing=outing,
                           opponent=opponent,
                           this_season=this_season,
                           all_seasons=all_seasons,
                           this_pitcher=this_pitcher,
                           all_pitchers=all_pitchers,
                           form=form)

# ***************-DELETE OUTING-*************** #
@outing.route('/delete_outing/<id>', methods=['GET', 'POST'])
@login_required
def delete_outing(id):
    '''
    DELETE OUTING
    Can delete an existing outing through this function

    PARAM:
        -id: the outing id (primary key) in which the user
            wants to delete

    RETURN:
        -deletes the outing and redirects to user page which the outing
            was associated with
    '''

    # get the outing and user objects associated with this outing
    outing = Outing.query.filter_by(id=id).first_or_404()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))
    user = User.query.filter_by(id=outing.user_id).first_or_404()

    # only admins have permission to delete an outing
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('main.index'))

    # deletes the pitches associated with outing
    for at_bat in outing.at_bats:
        for p in at_bat.pitches:
            db.session.delete(p)
        db.session.delete(at_bat)

    # deletes the outing iteself and commits changes to database
    db.session.delete(outing)
    db.session.commit()

    # redirects to user page associated with deletion
    flash('Outing has been deleted')
    return redirect(url_for('pitcher.pitcher_home', id=user.id))


# ***************-NEW OUTING CSV-*************** #
@outing.route('/new_outing_csv', methods=['GET', 'POST'])
@login_required
def new_outing_csv():
    '''
    NEW OUTING CSV

    PARAM:
        -NONE

    RETURN:
        -
    '''

    form = NewOutingFromCSV()
    form.pitcher.choices = getAvailablePitchers()

    if form.validate_on_submit():

        # Get upload filename and save it to a temp file we can work with
        file_name = form.file.data.filename
        file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                "csv_files",
                                file_name)

        # save the file with its current name
        form.file.data.save(file_loc)

        # WIP make it so that duplicate file names dont appear
        # while os.path.isfile(file_loc):
        #     file_name = file_name + random.randint()

        # Analyze *.csv file for errors and discrepencies
        if validate_CSV(file_loc):

            # gets the user associated the username of the pitcher the outing
            # is being created for
            user = User.query.filter_by(username=form.pitcher.data).first_or_404()

            # creates a new outing object based on form data and user
            outing = Outing(
                date=form.date.data,
                opponent_id=form.opponent.data.id,
                season_id=form.season.data.id,
                user_id=user.id)

            # add the new outing to the database before pitches so pitches
            # have a outing_id associated with them
            db.session.add(outing)
            db.session.commit()

            return redirect(url_for(
                'outing.new_outing_csv_pitches',
                file_name=file_name,
                outing_id=outing.id))
        else:  # delete invalid csv and refresh page
            os.remove(file_loc)
            return render_template("upload_csv.html",
                                   form=form)

    return render_template("csv/upload_csv.html",
                           form=form)


# ***************-NEW OUTING CSV PITCHES-*************** #
@outing.route('/new_outing_csv_pitches/<file_name>/<outing_id>',methods=['GET', 'POST'])
@login_required
def new_outing_csv_pitches(file_name, outing_id):
    '''
    NEW OUTING CSV

    PARAM:
        -NONE

    RETURN:
        -
    '''
    # location of file name, passed from new_outing_csv via GET
    file_loc = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "csv_files",
        file_name)

    # extract pitches from CSV so they can be put in html form
    pitches = []
    with open(file_loc) as f:
        csv_file = csv.DictReader(f)
        for index, row in enumerate(csv_file):
            pitch = {
                "velocity": row['velocity'],
                "lead_runner": row['lead_runner'],
                "time_to_plate": row['time_to_plate'],
                "pitch_type": row['pitch_type'],
                "pitch_result": row['pitch_result'],
                "hit_spot": row['hit_spot'],
                "traj": row['traj'],
                "ab_result": row['ab_result'],
                "fielder": row['fielder'],
                "inning": row['inning']
            }
            if 'batter_id' in row.keys():
                pitch["batter_id"] = row["batter_id"]
            pitches.append(pitch)

    # Retrieve required DB objects
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))
    user = User.query.filter_by(id=outing.user_id).first_or_404()
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first_or_404()
    season = Season.query.filter_by(id=outing.season_id).first_or_404()

    # Setup form and form variables
    form = NewOutingFromCSVPitches()
    # set up batter choices
    for subform in form.pitch:
        subform.batter_id.choices = getAvailableBatters(outing_id)
    # batter choices to fill into html
    batters = []
    for b in opponent.batters:
        batters.append(b)

    if form.validate_on_submit():

        # sets up count for first pitch of outing
        # sets up count for first pitch of outing
        if (season.semester == 'Fall'):
            balls = 1
            strikes = 1
        else:
            balls = 0
            strikes = 0
        count = f'{balls}-{strikes}'

        # Boolean variable to help with adding AtBat objects to the db
        new_at_bat = True

        # variable to hold the current AtBat object
        current_at_bat = None

        # add each individual pitch to the database
        for index, subform in enumerate(form.pitch):

            # get the batter_id for the AtBat and Pitch objects
            batter_id = subform.batter_id.data

            # if a new at bat has started, make a new AtBat object
            if new_at_bat:
                at_bat = AtBat(
                    batter_id=batter_id,
                    outing_id=outing_id)

                # Add the AtBat object to database
                db.session.add(at_bat)
                db.session.commit()

                # Set the current_at_bat for subsequent pitches accordingly
                current_at_bat = at_bat

                # So new at_bat variables aren't made every pitch
                new_at_bat = False

            # creates Pitch object based on subform data
            pitch_num = index + 1

            # create Pitch object
            pitch = Pitch(
                atbat_id=current_at_bat.id,
                pitch_num=pitch_num,
                batter_id=subform.batter_id.data,
                velocity=subform.velocity.data,
                lead_runner=subform.lead_runner.data,
                time_to_plate=subform.time_to_plate.data,
                pitch_type=subform.pitch_type.data,
                pitch_result=subform.pitch_result.data,
                hit_spot=subform.hit_spot.data,
                count=count,
                ab_result=subform.ab_result.data,
                traj=subform.traj.data,
                fielder=subform.fielder.data,
                inning=subform.inning.data)

            # update count based on current count and pitch result
            balls, strikes, count = updateCount(
                balls,
                strikes,
                pitch.pitch_result,
                pitch.ab_result,
                season)

            # adds pitch to database
            db.session.add(pitch)
            db.session.commit()

            if pitch.ab_result is not '':
                new_at_bat = True

        # delete temp file and be done with it
        os.remove(file_loc)

        flash("New Outing Created!")
        return redirect(url_for('main.index'))
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(err)

    return render_template("csv/new_outing_csv_pitches.html",
                           form=form,
                           pitches=pitches,
                           batters=batters)


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
