from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.forms import NewOutingFromCSV
from app.models import User, Outing, Pitch
from app.stats import calcPitchPercentages, pitchUsageByCount, calcAverageVelo
from app.stats import calcPitchStrikePercentage, calcPitchWhiffRate
from app.stats import createPitchPercentagePieChart, velocityOverTimeLineChart
from app.stats import pitchStrikePercentageBarChart
import csv
import os


# home page for portal, displays the roster
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    users = User.query.filter(User.year != 'Coach/Manager').all()
    return render_template('index.html', title='Home', users=users)


# login page for portal, only team members, coaches, etc. have logins
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # if the user is already signed in then send to home page
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():  # when the Login button is pressed

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

    return render_template('login.html', title='Sign In', form=form)

# Doesn't have a template associated. Just lets the user logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Registration page if an admin wants to add someone to roster
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
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
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

# User page where the outings that a player has thrown will show up
@app.route('/user/<username>')
@login_required
def user(username):
    # get the user object associated with the username in the url
    user = User.query.filter_by(username=username).first_or_404()

    # get the outings associated with that player
    outings = user.outings

    return render_template(
        'user.html',
        title='User',
        user=user,
        outings=outings)

# Page for someone to create a new outing either for themself or for another
# player if admin
@app.route('/new_outing', methods=['GET', 'POST'])
@login_required
def new_outing():
    form = OutingForm()

    # gets all the User objects that are players on the team
    pitchers_objects = User.query.filter(User.year != 'Coach/Manager').all()

    # set the available choices that someone can create an outing for
    available_pitchers = []
    # admins can create outings for anyone
    if (current_user.admin):
        for p in pitchers_objects:
            available_pitchers.append(
                (p.username, p.firstname + " " + p.lastname)
                )
    # if not an admin then can only create outing for yourself
    else:
        available_pitchers.append(
            (
                current_user.username,
                current_user.firstname+" "+current_user.lastname
                )
            )

    # set the choices made above
    form.pitcher.choices = available_pitchers

    # when the 'Create Outing' button is pressed
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

        # add each individual pitch to the database
        for subform in form.pitch:
            # creates Pitch object based on subform data
            pitch = Pitch(
                outing_id=outing.id,
                pitch_num=subform.pitch_num.data,
                batter_id=subform.batter_id.data,
                batter_hand=subform.batter_hand.data,
                velocity=subform.velocity.data,
                lead_runner=subform.lead_runner.data,
                time_to_plate=subform.time_to_plate.data,
                pitch_type=subform.pitch_type.data,
                pitch_result=subform.pitch_result.data,
                hit_spot=subform.hit_spot.data,
                count_balls=subform.count_balls.data,
                count_strikes=subform.count_strikes.data,
                result=subform.result.data,
                fielder=subform.fielder.data,
                hit=subform.hit.data,
                out=subform.out.data,
                inning=subform.inning.data)

            # adds pitch to database
            db.session.add(pitch)
            db.session.commit()

        # redirects back to home page after outing was successfully created
        flash("New Outing Created!")
        return redirect(url_for('index'))

    return render_template('new_outing.html', title='New Outing', form=form)

# Displays the pitches and statistics from a certain outing
@app.route('/outing/<outing_id>', methods=['GET', 'POST'])
@login_required
def outing(outing_id):
    # get the outing object associated by the id in the url
    outing = Outing.query.filter_by(id=outing_id).first_or_404()

    # Get statistical data
    usages, usage_percentages = calcPitchPercentages(outing)
    counts, counts_percentages = pitchUsageByCount(outing)
    pitch_avg_velo = calcAverageVelo(outing)
    pitch_strike_percentage = calcPitchStrikePercentage(outing)
    pitch_whiff = calcPitchWhiffRate(outing)

    # Get statistical graphics
    usage_percentages_pie_chart = createPitchPercentagePieChart(
        usage_percentages)
    velocity_over_time_line_chart = velocityOverTimeLineChart(outing)
    strike_percentage_bar_chart = pitchStrikePercentageBarChart(
        pitch_strike_percentage)

    return render_template(
        'outing.html',
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
        strike_percentage_bar_chart=strike_percentage_bar_chart
        )

# Page to edit an outing already stored in database
@app.route('/edit_outing/<outing_id>', methods=['GET', 'POST'])
@login_required
def edit_outing(outing_id):
    # get the outing and user objects associated with this outing
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    user = User.query.filter_by(id=outing.user_id).first_or_404()

    # only admins and players themselves can go back and edit outing data
    if (not current_user.admin) and (current_user.username != user.username):
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('index'))

    # get correct form and don't allow a change to be made to pitcher of outing
    form = OutingForm()
    form.pitcher.choices = [(
        user.firstname+" "+user.lastname,
        user.firstname+" "+user.lastname)]

    # when edit wants to be made
    if form.validate_on_submit():
        # delete all of the pitche associated with the outing
        for p in outing.pitches:
            db.session.delete(p)

        # delete the outing itself and commit changes
        db.session.delete(outing)
        db.session.commit()

        # create a new Outing object based on the form and put in database
        outing_edited = Outing(date=form.date.data,
                               opponent=form.opponent.data,
                               season=form.season.data,
                               user_id=user.id)
        db.session.add(outing_edited)
        db.session.commit()

        # add each individual pitch to the database
        for subform in form.pitch:

            # creates Pitch object based on subform data
            pitch = Pitch(
                outing_id=outing_edited.id,
                pitch_num=subform.pitch_num.data,
                batter_id=subform.batter_id.data,
                batter_hand=subform.batter_hand.data,
                velocity=subform.velocity.data,
                lead_runner=subform.lead_runner.data,
                time_to_plate=subform.time_to_plate.data,
                pitch_type=subform.pitch_type.data,
                pitch_result=subform.pitch_result.data,
                hit_spot=subform.hit_spot.data,
                count_balls=subform.count_balls.data,
                count_strikes=subform.count_strikes.data,
                result=subform.result.data,
                fielder=subform.fielder.data,
                hit=subform.hit.data,
                out=subform.out.data,
                inning=subform.inning.data)

            # adds pitch to database
            db.session.add(pitch)
            db.session.commit()

        # redirect to user page
        flash('The outing has been adjusted!')
        return redirect(url_for('user', username=user.username))

    # sets up subforms so they are visible in edit_outing.html
    for p in range(0, outing.pitches.count()-1):
        form.pitch.append_entry()

    return render_template(
        'edit_outing.html',
        title='Edit Outing',
        outing=outing, form=form)

# page to delete outing. No template associated. Just allows user
# to delete an outing
@app.route('/delete_outing/<outing_id>', methods=['GET', 'POST'])
@login_required
def delete_outing(outing_id):
    # get the outing and user objects associated with this outing
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    user = User.query.filter_by(id=outing.user_id).first_or_404()

    # only admins and players themselves to delete an outing
    if (not current_user.admin) and (current_user != user.username):
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


@app.route('/new_outing_csv', methods=['GET', 'POST'])
@login_required
def new_outing_csv():
    form = NewOutingFromCSV()

    # get the pitcehes that this user is allowed to make outings for
    form.pitcher.choices = getAvailablePitchers()

    if form.validate_on_submit():

        # sets username variable
        username = form.pitcher.data
        user = User.query.filter_by(username=username).first_or_404()

        # Get upload filename and save it to a temp file we can work with
        file_name = form.file.data.filename
        file_loc = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "csv_files",
                file_name
            )
        form.file.data.save(file_loc)

        # Analyze *.csv file for errors and discrepencies
        with open(file_loc) as f:
            csv_file = csv.DictReader(f)

        return redirect(url_for('new_outing_csv'))
    else:
        print("failed to validate")

    return render_template("upload_csv.html", form=form)


# BEGIN UTILITY FUNCTIONS FOR ROUTES
# -------------------------------------------------------------------------------
def getAvailablePitchers():
    """Gets all of the string names you are allowed to create outings for

    Returns:
        [array] -- [strings of pitchers names]
    """

    # gets all the User objects that are players on the team
    pitchers_objects = User.query.filter(User.year != 'Coach/Manager').all()

    # set the available choices that someone can create an outing for
    available_pitchers = []
    # admins can create outings for anyone
    if (current_user.admin):
        for p in pitchers_objects:
            available_pitchers.append(
                (p.username, p.firstname + " " + p.lastname)
                )
    # if not an admin then can only create outing for yourself
    else:
        available_pitchers.append(
            (
                current_user.username,
                current_user.firstname+" "+current_user.lastname
                )
            )

    return available_pitchers
