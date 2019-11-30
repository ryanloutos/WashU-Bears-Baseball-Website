from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.models import User, Outing, Pitch


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    users = User.query.all()
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
                    email=form.email.data)
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

@app.route('/new_outing/<username>', methods=['GET', 'POST'])
@login_required
def new_outing(username):
    form = OutingForm()
    user = User.query.filter_by(username=username).first_or_404()
    if form.validate_on_submit():
        outing = Outing(date = form.date.data,
                        opponent = form.opponent.data,
                        season = form.season.data,
                        user_id = user.id)
        db.session.add(outing)
        db.session.commit()
        return redirect(url_for('new_outing_pitches', outing=outing.id))
    return render_template('new_outing.html', title='New Outing', form=form, user=user)

@app.route('/new_outing_pitches/<outing>', methods=['GET', 'POST'])
@login_required
def new_outing_pitches(outing):
    form = PitchForm()
    if form.validate_on_submit():
        flash("YES")
        pitch = Pitch(outing_id = outing,
                      pitch_num = form.pitch_num.data,
                      batter_id = form.batter_id.data,
                      batter_hand = form.batter_hand.data,
                      velocity = form.velocity.data,
                      lead_runner = form.lead_runner.data,
                      time_to_plate = form.time_to_plate.data,
                      pitch_type = form.pitch_type.data,
                      pitch_result = form.pitch_result.data,
                      hit_spot = form.hit_spot.data,
                      count_balls = form.count_balls.data,
                      count_strikes = form.count_strikes.data,
                      result = form.result.data,
                      fielder = form.fielder.data,
                      hit = form.hit.data,
                      out = form.out.data,
                      inning = form.inning.data)
        db.session.add(pitch)
        db.session.commit()
        flash("YES")
        return redirect(url_for('index'))
    else:
        flash("NO GO")
        return render_template('new_outing_pitches.html', form=form, outing=outing)