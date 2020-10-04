from app import db

from flask import flash
from flask import request
from flask import url_for
from flask import redirect
from flask import Blueprint
from flask import render_template

from app.forms import User
from app.forms import LoginForm
from app.forms import EditUserForm
from app.forms import RegistrationForm
from app.forms import ChangePasswordForm
from app.forms import AdminForceChangePasswordForm

from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

from werkzeug.urls import url_parse

main = Blueprint('main', __name__)

# ***************-INDEX-*************** #
@main.route('/')
@main.route('/index')
@login_required
def index():
    return render_template(
        'main/index.html',
        title='WashU Baseball'
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
        user=user,
        title="Profile"
    )

# ***************-CHANGE PASSWORD-*************** #
@main.route('/user/<id>/change_password', methods=['GET', 'POST'])
@login_required
def change_password(id):
    user = User.query.filter_by(id=id).first()

    if not user:
        flash("URL does not exist")
        return redirect(url_for("main.index"))

    # if someone tries to access link directly
    if current_user.id != user.id:
        flash("You can only make changes to your own account")
        return redirect(url_for("main.index"))

    form = ChangePasswordForm()
    if form.validate_on_submit():

        if not user.check_password(form.current_password.data):
            flash("Current password entered is incorrect")
            return redirect(url_for("main.change_password", id=user.id))

        user.set_password(form.password.data)

        db.session.commit()

        flash('Password changed!')
        return redirect(url_for('main.user', id=user.id))

    return render_template(
        'main/change_password.html',
        title='Change Password',
        form=form
    )

# ***************-EDIT USER-*************** #
@main.route('/user/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.filter_by(id=id).first()

    if not user:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    # if someone tries to access link directly
    if current_user.id != user.id:
        flash("You can only make changes to your own account")
        return redirect(url_for("main.index"))

    form = EditUserForm()
    if form.validate_on_submit():

        user.username = form.username.data
        user.email = form.email.data

        db.session.commit()

        flash('Changes made!')
        return redirect(url_for('main.user', id=current_user.id))

    return render_template(
        'main/edit_user.html',
        title='Edit User',
        user=user,
        form=form
    )

# ***************-LOGIN-*************** #
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))

        login_user(user)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template(
        'main/login.html',
        title="Login",
        form=form
    )

# ***************-LOGOUT-*************** #
@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# ***************-REGISTER-*************** #
@main.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if not current_user.admin:
        flash("Admin feature only!")
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():

        user = User(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            username=form.username.data,
            email=form.email.data,
            admin=form.admin.data,
            retired=form.retired.data,
            current_coach=form.current_coach.data,
            current_player=form.current_player.data
        )

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("New user created!")
        return redirect(url_for("main.login"))

    return render_template(
        "main/register.html",
        title="Register",
        form=form
    )


@main.route("/view_users", methods=["GET", "POST"])
@login_required
def view_users():

    if not current_user.admin:
        flash("Admin privileges Required ")
        return redirect(url_for("main.index"))

    users = User.query.all()
    return render_template(
        "main/view_users.html",
        title="View Current Users",
        users=users
    )


@main.route("/admin_password_change/<user_id>", methods=["GET", "POST"])
@login_required
def admin_password_change(user_id):
    if not current_user.admin:
        flash("Admin privileges Required")
        return redirect(url_for("main.index"))

    u = User.query.filter_by(id=user_id).first()

    form = AdminForceChangePasswordForm()
    if form.validate_on_submit():

        # set the new password
        u.set_password(form.password.data)

        # commit the changes
        db.session.commit()

        # redirects to user page
        flash('Password changed!')
        return redirect(url_for('main.view_users'))

    return render_template(
        "main/admin_password_change.html",
        title="Admin Password Change",
        form=form,
        user=u
    )
