from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.models import User, Outing, Pitch
from app.stats import calcPitchPercentages, pitchUsageByCount


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    users = User.query.filter(User.year != 'Coach/Manager').all()
    return render_template('index.html', title='Home', users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(firstname=form.firstname.data,
                    lastname=form.lastname.data,
                    year=form.year.data,
                    throws=form.throws.data,
                    username=form.username.data,
                    email=form.email.data,
                    admin=form.admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    outings = user.outings
    return render_template(
        'user.html',
        title='User',
        user=user,
        outings=outings)

@app.route('/new_outing', methods=['GET', 'POST'])
@login_required
def new_outing():
    form = OutingForm()
    pitchers_objects = User.query.filter(User.year != 'Coach/Manager').all()
    available_pitchers = []
    if (current_user.admin):
        for p in pitchers_objects:
            available_pitchers.append((p.username, p.firstname + " " + p.lastname))
    else:
        available_pitchers.append((current_user.username, current_user.firstname+" "+current_user.lastname))
    form.pitcher.choices = available_pitchers
    if form.validate_on_submit():
        if (current_user.admin):
            username = form.pitcher.data
        else:  
            username = current_user.username
        user = User.query.filter_by(username=username).first_or_404()
        outing = Outing(date = form.date.data,
                        opponent = form.opponent.data,
                        season = form.season.data,
                        user_id = user.id)
        db.session.add(outing)
        db.session.commit()
        for subform in form.pitch:
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
            db.session.add(pitch)
            db.session.commit()
        flash("New Outing Created!")
        return redirect(url_for('index'))
    return render_template('new_outing.html', title='New Outing', form=form)


@app.route('/outing/<outing_id>', methods=['GET', 'POST'])
@login_required
def outing(outing_id):
    outing = Outing.query.filter_by(id=outing_id).first_or_404()

    # Get statistical data
    usages,usage_percentages = calcPitchPercentages(outing)
    counts, counts_percentages = pitchUsageByCount(outing)

    return render_template(
        'outing.html',
        outing=outing,
        usages=usages,
        usage_percentages=usage_percentages,
        counts=counts,
        counts_percentages=counts_percentages
        )

@app.route('/edit_outing/<outing_id>', methods=['GET', 'POST'])
@login_required
def edit_outing(outing_id):
    form = OutingForm()
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    pitcher = User.query.filter_by(id=outing.user_id).first_or_404()
    form.pitcher.choices = [(pitcher.firstname+" "+pitcher.lastname, pitcher.firstname+" "+pitcher.lastname)]
    for p in outing.pitches:
        if p.pitch_num != 1:
            form.pitch.append_entry()
    if form.validate_on_submit():
        user = User.query.filter_by(id=outing.user_id).first_or_404()
        for p in outing.pitches:
            db.session.delete(p)
        db.session.delete(outing)
        db.session.commit()
        outing_edited = Outing(date = form.date.data,
                               opponent = form.opponent.data,
                               season = form.season.data,
                               user_id = user.id)
        db.session.add(outing_edited)
        db.session.commit()
        for subform in form.pitch:
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
            db.session.add(pitch)
            db.session.commit()
        flash('The outing has been adjusted!')
        return redirect(url_for('user', username=user.username))
    return render_template('edit_outing.html', outing=outing, form=form)