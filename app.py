from flask import Flask, render_template, url_for, redirect, flash
import mysql.connector
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
login = LoginManager(app)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootuserpassword",
    database="WashU_Pitching"
)

#sets up PLAYERS variable
players = []
cur = db.cursor()
cur.execute("SELECT firstname, lastname FROM Roster")
result = cur.fetchall()
for player in result:
    fullname = player[0]+" "+player[1]
    players.append((fullname,fullname))
    # players.append(fullname)
cur.close()

#sets up OUTINGS variable
outings = [dict() for x in range(0)]
outings_dropdown = []
cur = db.cursor()
cur.execute("SELECT * FROM Outings")
result = cur.fetchall()
cur.close()
for outing in result:
    date = outing[0]
    opponent = outing[2]
    season = outing[3]
    firstname = outing[4]
    lastname = outing[5]
    this_outing = {
        'pitcher': firstname+" "+lastname,
        'date': date,
        'season': season,
        'opponent': opponent
    }
    this_outing_dropdown = date+" "+opponent
    outings_dropdown.append((this_outing_dropdown, this_outing_dropdown))
    outings.append(this_outing)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SelectPlayer(FlaskForm):
    player_name = SelectField(u'Name', choices = players, validators=[DataRequired()])
    player_outing = SelectField('Outing', choices = outings_dropdown, validators=[DataRequired()])
    # which_statistic = SelectField('Stat', validators=[DataRequired()])
    go = SubmitField('Go')


# CURRENT LOGINS: ryanloutos ryanloutos, mitchellblack mitchellblack
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur = db.cursor()
        cur.execute("SELECT (password) FROM Login_Info WHERE username='{}'".format(form.username.data))
        result = cur.fetchall()
        if (result):
            if result[0][0] == form.password.data:
                # flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
                cur.close()
                return redirect(url_for('outing'))
            else:
                flash('Incorrect username or password')
                cur.close()
                return redirect(url_for('login'))
        else: 
            flash('Incorrect username or password')
            cur.close()
            return render_template('login.html', title='Sign In', form=form)
    return render_template('login.html', title='Sign In', form=form)


@app.route("/hello")
def hello_world():
    return "Hello"+players


@app.route("/home", methods=['GET', 'POST'])
def outing():
    form = SelectPlayer()
    if form.validate_on_submit():
        #do something here
        return render_template("home.html", form=SelectPlayer())
    return render_template("home.html", form=SelectPlayer())


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3456')

