from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.forms import NewOutingFromCSV, SeasonForm, OpponentForm, BatterForm
from app.forms import OutingPitchForm
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
    HOME PAGE
    Returns the home page of the portal

    PARAM:
        -None

    RETURN:
        -Displays index.html and passes the player names
            along with the seasons
    '''
    users = User.query.filter(User.year != 'Coach/Manager').all()
    seasons = Season.query.all()
    return render_template('main/index.html',
                           users=users,
                           seasons=seasons)

# ***************-LOGIN-*************** #
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    LOGIN PAGE
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
                           form=form)

# ***************-LOGOUT-*************** #
@app.route('/logout')
def logout():
    '''
    LOGOUT
    Logouts the current_user and redirects to login page

    PARAM:
        -None

    RETURN:
        -Login page
    '''
    logout_user()
    return redirect(url_for('login'))

# ***************-USER HOMEPAGE-*************** #
@app.route('/user/<username>')
@login_required
def user(username):
    '''
    USER HOMEPAGE
    Displays outings for a specific user

    PARAM:
        -username: the username of the player associated
            with the outing that will displayed

    RETURN:
        -user.html which displays the outings to be viewed
            that are associated with username
    '''
    # get the user object associated with the username in the url
    user = User.query.filter_by(username=username).first_or_404()

    # get the outings associated with that player
    outings = user.outings

    return render_template('main/user.html',
                           title='User',
                           user=user,
                           outings=outings)

# ***************-SEASON HOMEPAGE-*************** #
@app.route('/season/<id>')
@login_required
def season(id):
    '''
    SEASON HOMEPAGE

    PARAM:
        -id: The season id (primary key) of the season
            that is requested to be displayed

    RETURN:
        -season.html which displays all of the outings
            associated with that season
    '''

    # gets the Season object associated with the id parameter
    season = Season.query.filter_by(id=id).first_or_404()

    # outings associated with the specific season
    outings = season.outings

    return render_template('season/season.html',
                           title='Season',
                           season=season,
                           outings=outings)

# ***************-OUTING HOMEPAGE-*************** #
@app.route('/outing/<outing_id>', methods=['GET', 'POST'])
@login_required
def outing(outing_id):
    '''
    OUTING HOMEPAGE

    PARAM:
        -outing_id: The outing id (primary key) of the outing
            that is requested to be displayed

    RETURN:
        -outing.html which displays all of the info/pitches
            associated with that outing
    '''
    # get the outing object associated by the id in the url
    outing = Outing.query.filter_by(id=outing_id).first_or_404()

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

    # render template with all the statistical data calculated from
    # the outing
    return render_template('outing/outing.html',
                           title='Outing',
                           outing=outing,
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

# ***************-NEW USER-*************** #
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    '''
    REGISTER
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
                    year=form.year.data,
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
                           form=form)

# ***************-NEW SEASON-*************** #
@app.route('/new_season', methods=['GET', 'POST'])
@login_required
def new_season():
    '''
    NEW SEASON
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
                           form=form)

# ***************-NEW OPPONENT-*************** #
@app.route('/new_opponent', methods=['GET', 'POST'])
@login_required
def new_opponent():
    '''
    NEW OPPONENT
    Can create a new opponent for outings to be associated
    with

    PARAM:
        -None

    RETURN:
        -new_opponent.html and redirects to index page
            once a new opponent was successfully created
    '''
    # if user is not an admin, they can't create a new season
    if not current_user.admin:
        flash('You are not an admin and cannot create a opponent')
        return redirect(url_for('index'))

    # when the Create Season button is pressed...
    form = OpponentForm()
    if form.validate_on_submit():

        # insert data from form into season table
        opponent = Opponent(name=form.name.data)

        # send Season object to data table
        db.session.add(opponent)
        db.session.commit()

        #create the batter objects from the form and send to database
        for subform in form.batter:
            batter = Batter(
                name=subform.fullname.data,
                short_name=subform.nickname.data,
                bats=subform.bats.data,
                opponent_id=opponent.id
            )
            db.session.add(batter)
        
        #commit the batters to database
        db.session.commit()

        # redirect back to login page
        flash('Congratulations, you just made a new opponent!')
        return redirect(url_for('index'))

    return render_template('opponent/new_opponent.html', 
                           form=form)

# ***************-NEW OUTING-*************** #
@app.route('/new_outing', methods=['GET', 'POST'])
@login_required
def new_outing():
    '''
    NEW OUTING
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

        # sets the username variable accordingly
        username = form.pitcher.data

        # gets the user associated the username of the pitcher the outing
        # is being created for
        user = User.query.filter_by(username=username).first_or_404()

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

        # if "add pitches" button was clicked
        if form.validate_on_submit():

            # sets up count for first pitch of outing
            balls = 0
            strikes = 0
            count = f'{balls}-{strikes}'

            # add each individual pitch to the database
            for index, subform in enumerate(form.pitch):

                # sets the pitch_num column automatically
                pitch_num = index+1

                # create Pitch object
                pitch = Pitch(outing_id=outing_id,
                              pitch_num=pitch_num,
                              batter_id=subform.batter_id.data,
                              batter_hand=subform.batter_hand.data,
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
                                                    pitch.ab_result)

                # adds pitch to database
                db.session.add(pitch)
                db.session.commit()

            flash('Pitches added to outing!')
            return redirect(url_for('outing', outing_id=outing_id))

        return render_template('outing/new_outing_pitches.html',
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

        # delete all of the pitches associated with the outing
        for p in outing.pitches:
            db.session.delete(p)

        # commit the changes
        db.session.commit()

        # set up count variable to update with each pitch
        balls = 0
        strikes = 0
        count = '0-0'

        # add each individual pitch to the database
        for index, subform in enumerate(form.pitch):

            # sets pitch_num automatically
            pitch_num = index+1

            # creates Pitch object based on subform data
            pitch = Pitch(outing_id=outing_id,
                          pitch_num=pitch_num,
                          batter_id=subform.batter_id.data,
                          batter_hand=subform.batter_hand.data,
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

            # updates the count based on previous pitch
            balls, strikes, count = updateCount(balls,
                                                strikes,
                                                pitch.pitch_result,
                                                pitch.ab_result)

            # adds pitch to database
            db.session.add(pitch)
            db.session.commit()

        # redirect to user page
        flash('The outing has been adjusted!')
        return redirect(url_for('user', username=user.username))

    # sets up subforms so they are visible in edit_outing.html
    for p in range(1, outing.pitches.count()):
        form.pitch.append_entry()

    # set up batter choices here
    for subform in form.pitch:
        subform.batter_id.choices = getAvailableBatters(outing_id)
    
    batters = []
    for b in opponent.batters:
        batters.append(b)

    return render_template('outing/edit_outing_pitches.html',
                           title='Edit Outing',
                           batters=batters,
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
    all_pitchers = User.query.filter(User.year != 'Coach/Manager').all()

    # only admins can go back and edit outing data
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('index'))

    # when edit wants to be made
    if form.validate_on_submit():
        
        # get the user object associated with the pitcher submitted in form
        user = User.query.filter_by(username=form.pitcher.data).first_or_404()

        # commit the changes
        db.session.delete(outing)
        db.session.commit()

        outing_edited = Outing(date=form.date.data,
                               opponent_id=opponent.id,
                               user_id=user.id,
                               season_id=form.season.data.id)

        # set up count variable to update with each pitch
        balls = 0
        strikes = 0
        count = '0-0'

        # adjust the pitches with the new outing id
        for pitch in outing.pitches:

            # creates Pitch object based on subform data
            new_pitch = Pitch(outing_id=outing_edited.id,
                              pitch_num=pitch.pitch_num,
                              batter_id=pitch.batter_id,
                              batter_hand=pitch.batter_hand,
                              velocity=pitch.velocity,
                              lead_runner=pitch.lead_runner,
                              time_to_plate=pitch.time_to_plate,
                              pitch_type=pitch.pitch_type,
                              pitch_result=pitch.pitch_result,
                              hit_spot=pitch.hit_spot,
                              count=pitch.count,
                              ab_result=pitch.ab_result,
                              traj=pitch.traj,
                              fielder=pitch.fielder,
                              inning=pitch.inning)

            # adds pitch to database and delete old pitch
            db.session.add(new_pitch)
            db.session.delete(pitch)

        db.session.add(outing_edited)
        db.session.commit()

        # redirect to user page
        flash('The outing has been adjusted!')
        return redirect(url_for('user', username=user.username))

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
@app.route('/delete_outing/<outing_id>', methods=['GET', 'POST'])
@login_required
def delete_outing(outing_id):
    '''
    DELETE OUTING
    Can delete an existing outing through this function

    PARAM:
        -outing_id: the outing id (primary key) in which the user
            wants to delete

    RETURN:
        -deletes the outing and redirects to user page which the outing
            was associated with
    '''

    # get the outing and user objects associated with this outing
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    user = User.query.filter_by(id=outing.user_id).first_or_404()

    # only admins have permission to delete an outing
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('index'))

    # deletes the pitches associated with outing
    for p in outing.pitches:
        db.session.delete(p)

    # deletes the outing iteself and commits changes to database
    db.session.delete(outing)
    db.session.commit()

    # redirects to user page associated with deletion
    flash('Outing has been deleted')
    return redirect(url_for('user', username=user.username))

# ***************-NEW OUTING CSV-*************** #
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
        valid = validate_CSV(file_loc)
        if valid:
            return redirect(url_for('new_outing_csv_pitches', file_name=file_name))
        else:  # delete invalid csv and refresh page
            os.remove(file_loc)
            return render_template("upload_csv.html",
                                   form=form)

    return render_template("csv/upload_csv.html",
                           form=form)

# ***************-NEW OUTING CSV PITCHES-*************** #
@app.route('/new_outing_csv_pitches/<file_name>', methods=['GET', 'POST'])
@login_required
def new_outing_csv_pitches(file_name):
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
                "batter_id": row['batter_id'],
                "batter_hand": row['batter_hand'],
                "velocity": row['velocity'],
                "lead_runner": row['lead_runner'],
                "time_to_plate": row['time_to_plate'],
                "pitch_type": row['pitch_type'],
                "pitch_result": row['pitch_result'],
                "hit_spot": row['hit_spot'],
                "result": row['result'],
                "fielder": row['fielder'],
                "hit": row['hit'],
                "out": row['out'],
                "inning": row['inning']
            }
            pitches.append(pitch)

    form = OutingForm()
    form.pitcher.choices = getAvailablePitchers()

    if form.validate_on_submit():
        # sets the username variable accordingly
        if (current_user.admin):
            username = form.pitcher.data
        else:
            username = current_user.username

        # gets the user associated the username of the pitcher the outing
        # is being created for
        user = User.query.filter_by(username=username).first_or_404()

        # creates a new outing object based on form data and user
        outing = Outing(date=form.date.data,
                        opponent=form.opponent.data,
                        season=form.season.data,
                        user_id=user.id)

        # add the new outing to the database before pitches so pitches have a
        # outing_id associated with them
        db.session.add(outing)
        db.session.commit()

        balls = 0
        strikes = 0
        # add each individual pitch to the database
        for index, subform in enumerate(form.pitch):

            # creates Pitch object based on subform data
            pitchNum = index+1

            pitch = Pitch(outing_id=outing.id,
                          pitch_num=pitchNum,
                          batter_id=subform.batter_id.data,
                          batter_hand=subform.batter_hand.data,
                          velocity=subform.velocity.data,
                          lead_runner=subform.lead_runner.data,
                          time_to_plate=subform.time_to_plate.data,
                          pitch_type=subform.pitch_type.data,
                          pitch_result=subform.pitch_result.data,
                          hit_spot=subform.hit_spot.data,
                          count_balls=balls,
                          count_strikes=strikes,
                          result=subform.result.data,
                          fielder=subform.fielder.data,
                          hit=subform.hit.data,
                          out=subform.out.data,
                          inning=subform.inning.data)

            if pitch.result is not '':
                balls = 0
                strikes = 0
            else:
                if pitch.pitch_result is 'B':
                    balls += 1
                else:
                    if strikes is not 2:
                        strikes += 1

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
                           pitches=pitches)


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
    pitchers_objects = User.query.filter(User.year != 'Coach/Manager').all()

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
            "batter_id", "batter_hand", "velocity", "lead_runner",
            "time_to_plate", "pitch_type", "pitch_result", "hit_spot",
            "result", "fielder", "hit", "out", "inning"]
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

def updateCount(balls, strikes, pitch_result, ab_result):
    if ab_result is not '':
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
