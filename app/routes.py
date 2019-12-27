from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.forms import NewOutingFromCSV, SeasonForm, OpponentForm, BatterForm
from app.forms import OutingPitchForm, NewOutingFromCSVPitches
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat
from app.stats import calcPitchPercentages, pitchUsageByCount, calcAverageVelo
from app.stats import calcPitchStrikePercentage, calcPitchWhiffRate
from app.stats import createPitchPercentagePieChart, velocityOverTimeLineChart
from app.stats import pitchStrikePercentageBarChart
from app.stats import pitchUsageByCountLineCharts
# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random

# ***************-INDEX-*************** #
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    '''
    HOME PAGE:
    Returns the home page of the portal

    PARAM:
        -None

    RETURN:
        -Displays index.html and passes pitchers, opponents,
            seasons, and batters as a way to filter data
    '''
    pitchers = User.query.filter(User.grad_year != 'Coach/Manager').order_by(User.lastname).all()
    seasons = Season.query.all()
    batters = Batter.query.all()
    opponents = Opponent.query.all()

    return render_template('main/index.html',
                           title='WashU',
                           pitchers=pitchers,
                           opponents=opponents,
                           seasons=seasons,
                           batters=batters)

# ***************-LOGIN-*************** #
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    LOGIN PAGE:
    User enters username and password and gets
    redirected to index.html if successful

    PARAM:
        -None

    RETURN:
        -Displays login.html and redirects to index.html or some
            other page trying to be accessed once login is
            successful
    '''
    # if the user is already signed in then send to home page
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    # when the Login button is pressed
    if form.validate_on_submit():

        # get the user object from the username that was typed in
        user = User.query.filter_by(username=form.username.data).first()

        # if the username doesn't exist or passwords don't match,
        # redirect back to login page
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        # login the user if nothing failed above
        login_user(user, remember=form.remember_me.data)

        # send user to the page they were trying to get to without logging in
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('main/login.html',
                           title="Login",
                           form=form)

# ***************-LOGOUT-*************** #
@app.route('/logout')
def logout():
    '''
    LOGOUT:
    Logouts the current_user and redirects to login page

    PARAM:
        -None

    RETURN:
        -Login page
    '''
    logout_user()
    return redirect(url_for('login'))

# ***************-REGISTER-*************** #
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    '''
    REGISTER:
    Create a new user (player/coach/manager) if current user
    is an admin

    PARAM:
        -None

    RETURN:
        -register.html to create a new user and then
            redirects back to index.html once the user
            was created successfully
    '''
    # if user is not an admin, they can't add player/coach to portal
    if not current_user.admin:
        flash('You are not an admin and cannot create a user')
        return redirect(url_for('index'))

    # when the 'register' button is pressed
    form = RegistrationForm()
    if form.validate_on_submit():
        # takes in the data from the form and creates a User object (row)
        user = User(firstname=form.firstname.data,
                    lastname=form.lastname.data,
                    grad_year=form.year.data,
                    throws=form.throws.data,
                    username=form.username.data,
                    email=form.email.data,
                    admin=form.admin.data)

        # sets the password based on what was entered
        user.set_password(form.password.data)

        # adds new user to database
        db.session.add(user)
        db.session.commit()

        # redirects to login page
        flash('Congratulations, you just created a new user!')
        return redirect(url_for('login'))

    return render_template('main/register.html',
                           title='Register',
                           form=form)

# ***************-PITCHER HOMEPAGE-*************** #
@app.route('/pitcher/<id>', methods=['GET', 'POST'])
@login_required
def pitcher(id):
    '''
    PITCHER HOMEPAGE:
    Displays outings for a specific pitcher

    PARAM:
        -id: the id (primary key) of the pitcher that wants
            to be viewed

    RETURN:
        -pitcher.html which displays the outings to be viewed
            that are associated with username
    '''
    # get the user object associated with the username in the url
    pitcher = User.query.filter_by(id=id).first()

    # either bug or user trying to access pitcher page that DNE
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('index'))

    # if pitcher is a coach/manager, redirect to index page
    if pitcher.grad_year == 'Coach/Manager':
        flash('Cannot show outings for Coach/Manager')
        return redirect(url_for('index'))

    # get the outings associated with that player
    outings = pitcher.outings

    return render_template('main/pitcher.html',
                           title=pitcher,
                           pitcher=pitcher)

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
        return redirect(url_for('index'))

    # outings associated with the specific season
    outings = Outing.query.filter_by(season_id=id).order_by(Outing.date).all()

    return render_template('season/season.html',
                           title=season,
                           outings=outings,
                           season=season)

# ***************-OUTING HOMEPAGE-*************** #
@app.route('/outing/<id>', methods=['GET', 'POST'])
@login_required
def outing(id):
    '''
    OUTING HOMEPAGE:

    PARAM:
        -outing_id: The outing id (primary key) of the outing
            that is requested to be displayed

    RETURN:
        -outing.html which displays all of the info/pitches
            associated with that outing
    '''
    # get the outing object associated by the id in the url
    outing = Outing.query.filter_by(id=id).first()
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first()

    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('index'))

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
        'outing/outing.html',
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
        usage_percent_by_count_line_chart=usage_percent_by_count_line_chart)

# ***************-BATTER HOMEPAGE-*************** #
@app.route('/batter/<id>', methods=['GET', 'POST'])
@login_required
def batter(id):
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
        return redirect(url_for('index'))

    return render_template('opponent/batter.html',
                           title=batter,
                           batter=batter)

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

    # bug or user trying to view opponent that DNE
    if not opponent:
        flash("URL does not exist")
        return redirect(url_for('index'))

    return render_template('opponent/opponent.html',
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
        return redirect(url_for('index'))

    # when the Create Season button is pressed...
    form = SeasonForm()
    if form.validate_on_submit():

        # insert data from form into season table
        season = Season(semester=form.semester.data,
                        year=form.year.data)

        # send Season object to data table
        db.session.add(season)
        db.session.commit()

        # redirect back to login page
        flash('Congratulations, you just made a new season!')
        return redirect(url_for('index'))

    return render_template('season/new_season.html',
                           title='New Season',
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
        return redirect(url_for('index'))

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
        return redirect(url_for('index'))

    return render_template('opponent/new_opponent.html',
                           title='New Opponent',
                           form=form)

# ***************-NEW BATTER-*************** #
@app.route('/new_batter/<opponent_id>', methods=['GET', 'POST'])
@login_required
def new_batter(opponent_id):
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
        return redirect(url_for('index'))

    # when the Create Season button is pressed...
    form = BatterForm()
    if form.validate_on_submit():

        # insert data from form into season table
        batter = Batter(name=form.fullname.data,
                        short_name=form.nickname.data,
                        bats=form.bats.data,
                        grad_year=form.grad_year.data,
                        opponent_id=opponent_id)

        # send Season object to data table
        db.session.add(batter)
        db.session.commit()

        # redirect back to login page
        flash('Congratulations, you just made a new batter!')
        return redirect(url_for('opponent', id=opponent_id))

    return render_template('opponent/new_batter.html',
                           title='New Batter',
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
        return redirect(url_for('index'))

    # get opponent object
    opponent = Opponent.query.filter_by(id=id).first()

    # either bug or admin trying to edit opponent that doesn't exist
    if not opponent:
        flash('URL does not exist')
        return redirect(url_for('index'))

    # once 'create opponent' button is pressed
    form = OpponentForm()
    if form.validate_on_submit():

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

# ***************-EDIT BATTER-*************** #
@app.route('/edit_batter/<id>', methods=['GET', 'POST'])
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
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('index'))

    # get the correct form
    form = BatterForm()

    # get the batter object
    batter = Batter.query.filter_by(id=id).first()

    # bug or trying to edit batter that doesn't exist
    if not batter:
        flash('URL does not exist')
        return redirect(url_for('index'))

    # submit is clicked
    if form.validate_on_submit():

        # update info with data from form
        batter.name = form.fullname.data
        batter.short_name = form.nickname.data
        batter.bats = form.bats.data
        batter.grad_year = form.grad_year.data

        # commit the changes
        db.session.commit()

        flash('Batter has been adjusted')
        return redirect(url_for('index'))

    return render_template('opponent/edit_batter.html',
                           title='Edit Batter',
                           batter=batter,
                           form=form)

# ***************-DELETE BATTER-*************** #
@app.route('/delete_batter/<id>', methods=['GET', 'POST'])
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
        return redirect(url_for('index'))

    # get the batter object associated with the id
    batter = Batter.query.filter_by(id=id).first()

    # bug of trying to delete batter that doesn't exist
    if not batter:
        flash("Can't delete a batter that doesn't exist")
        return redirect(url_for('index'))

    # delete the batter from database
    db.session.delete(batter)
    db.session.commit()

    return redirect(url_for('opponent', id=batter.opponent_id))

# ***************-NEW OUTING-*************** #
@app.route('/new_outing', methods=['GET', 'POST'])
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
@app.route('/new_outing_pitches/<outing_id>', methods=['GET', 'POST'])
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
            pitch_num = index+1

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
        form=form)

# ***************-EDIT OUTING PITCHES-*************** #
@app.route('/edit_outing_pitches/<outing_id>', methods=['GET', 'POST'])
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
    user = User.query.filter_by(id=outing.user_id).first_or_404()
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first_or_404()
    season = Season.query.filter_by(id=outing.season_id).first_or_404()

    # only admins can go back and edit outing data
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('index'))

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
            pitch_num = index+1

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
@app.route('/edit_outing/<outing_id>', methods=['GET', 'POST'])
@login_required
def edit_outing(outing_id):

    # get correct form
    form = OutingForm()

    # get the available pitchers to choose from
    form.pitcher.choices = getAvailablePitchers()

    # get objects from database
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first_or_404()
    this_season = Season.query.filter_by(id=outing.season_id).first_or_404()
    all_seasons = Season.query.all()
    this_pitcher = User.query.filter_by(id=outing.user_id).first_or_404()
    all_pitchers = User.query.filter(User.grad_year != 'Coach/Manager').all()

    # only admins can go back and edit outing data
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('index'))

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
        return redirect(url_for('pitcher', id=pitcher.id))

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
@app.route('/delete_outing/<id>', methods=['GET', 'POST'])
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
    user = User.query.filter_by(id=outing.user_id).first_or_404()

    # only admins have permission to delete an outing
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('index'))

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
    return redirect(url_for('pitcher', id=user.id))

# ***************-NEW OUTING CSV-*************** # MITCH
@app.route('/new_outing_csv', methods=['GET', 'POST'])
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
                'new_outing_csv_pitches',
                file_name=file_name,
                outing_id=outing.id))
        else:  # delete invalid csv and refresh page
            os.remove(file_loc)
            return render_template("upload_csv.html",
                                   form=form)

    return render_template("csv/upload_csv.html",
                           form=form)


# ***************-NEW OUTING CSV PITCHES-*************** # MITCH
@app.route(
    '/new_outing_csv_pitches/<file_name>/<outing_id>',
    methods=['GET', 'POST'])
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
            pitch_num = index+1

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

        # delete temp file and be done with it
        os.remove(file_loc)

        flash("New Outing Created!")
        return redirect(url_for('index'))
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
            "velocity", "lead_runner",
            "time_to_plate", "pitch_type", "pitch_result", "hit_spot",
            "ab_result", "traj", "fielder", "inning"]
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
