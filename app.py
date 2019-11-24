from flask import Flask, render_template, url_for, redirect, flash
import mysql.connector
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootuserpassword",
    database="WashU_Pitching"
)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# App routes
@app.route("/")
def index_page():
    return "index page"


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
                return render_template('index.html')
            else:
                flash('Incorrect username or password')
                cur.close()
                return render_template('login.html', title='Sign In', form=form)
        else: 
            flash('Incorrect username or password')
            cur.close()
            return render_template('login.html', title='Sign In', form=form)

    return render_template('login.html', title='Sign In', form=form)

@app.route("/hello")
def hello_world():
    return "Hello"+players


@app.route("/user/<username>")
def show_user(username):
    return f"Hello {username}"


@app.route("/index")
def show_template():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3456')

