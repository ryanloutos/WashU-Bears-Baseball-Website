from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from ..forms import LoginForm, RegistrationForm
from ..forms import EditUserForm, ChangePasswordForm, User

main = Blueprint('main', __name__)

# ***************-INDEX-*************** #
@main.route('/')
@main.route('/index')
@login_required
def index():
    return render_template (
        'main/index.html',
        title='WashU Pitching'
    )

# ***************-PROFILE PAGE-*************** #
@main.route('/user/<id>', methods=['GET', 'POST'])
@login_required
def user(id):
    if current_user.id is not int(id):
        flash('You can only view your own profile page')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(id=id).first_or_404()

    return render_template(
        'main/user.html',
        user=user)

# *************** -CHANGE PASSWORD - *************** #
@main.route('/user/<id>/change_password', methods=['GET', 'POST'])
@login_required
def change_password(id):
    '''
    CHANGE PASSWORD:

    PARAM:
        -id: the id of the user

    RETURN:
        -change_password.html which serves a form to make changes
    '''

    user = User.query.filter_by(id=id).first()

    if not user:
        flash("URL does not exist")
        return redirect(url_for("main.index"))

    # if someone tries to access link directly
    if current_user.id != user.id:
        flash("You can only make changes to your own account")
        return redirect(url_for("main.index"))

    # when the 'save changes' button is pressed
    form = ChangePasswordForm()
    if form.validate_on_submit():

        if not user.check_password(form.current_password.data):
            flash("Current password entered is incorrect")
            return redirect(url_for("main.change_password", id=user.id))

        # set the new password
        user.set_password(form.password.data)

        # commit the changes
        db.session.commit()

        # redirects to user page
        flash('Password changed!')
        return redirect(url_for('main.user', id=user.id))

    return render_template(
        'main/change_password.html',
        title='Change Password',
        form=form)

# *************** -EDIT USER - *************** #
@main.route('/user/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    '''
    EDIT USER:
    Change username/email associated with account

    PARAM:
        -id: the id of the user

    RETURN:
        -edit_user.html which serves a form to make changes
    '''

    user = User.query.filter_by(id=id).first()

    if not user:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    # if someone tries to access link directly
    if current_user.id != user.id:
        flash("You can only make changes to your own account")
        return redirect(url_for("main.index"))

    # when the 'save changes' button is pressed
    form = EditUserForm()
    if form.validate_on_submit():

        # update username and email
        user.username = form.username.data
        user.email = form.email.data

        # commit the changes
        db.session.commit()

        # redirects to user page
        flash('Changes made!')
        return redirect(url_for('main.user', id=current_user.id))

    return render_template('main/edit_user.html',
                           title='Edit User',
                           user=user,
                           form=form)

# ***************-LOGIN-*************** # DONE
@main.route('/login', methods=['GET', 'POST'])
def login():
    # if the user is already signed in then send to home page
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    # when the Login button is pressed
    if form.validate_on_submit():

        # get the user object from the username that was typed in
        user = User.query.filter_by(username=form.username.data).first()

        # if the username doesn't exist or passwords don't match,
        # redirect back to login page
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))

        # if the user is retired
        # if user.retired:
        #     flash("Retired pitcher, can't log in")
        #     return redirect(url_for('login'))

        # login the user if nothing failed above
        login_user(user)

        # send user to the page they were trying to get to without logging in
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('main/login.html',
                           title="Login",
                           form=form)

# ***************-LOGOUT-*************** # DONE
@main.route('/logout')
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
    return redirect(url_for('main.login'))

# ***************-REGISTER-*************** # DONE
@main.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('main.index'))

    # when the 'register' button is pressed
    form = RegistrationForm()
    if form.validate_on_submit():

        # takes in the data from the form and creates a User object (row)
        user = User(firstname=form.firstname.data,
                    lastname=form.lastname.data,
                    username=form.username.data,
                    email=form.email.data,
                    admin=form.admin.data,
                    retired=form.retired.data)

        # sets the password based on what was entered
        user.set_password(form.password.data)

        # adds new user to database
        db.session.add(user)
        db.session.commit()

        # redirects to login page
        flash('Congratulations, you just created a new user!')
        return redirect(url_for('main.login'))

    return render_template('main/register.html',
                           title='Register',
                           form=form)
