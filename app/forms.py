from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, IntegerField, IntegerField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

#Basic form for users to login, must type in both username and a password
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

#Creating a new account. 
class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    year = RadioField('Year', choices=[('FR','FR'),('SO','SO'),('JR','JR'),('SR','SR')], validators=[DataRequired()])
    throws = RadioField('Throws', choices=[('R','R'),('L','L')], validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()]) #Email() validator makes sure it's in email form
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(#make sure passwords match
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    #these two functions will run automatically when a new user is trying to be created
    def validate_username(self, username): #make sure username doesn't already exist in database
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email): #make sure email doesn't already exist in database
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

#Creating a new outing
class OutingForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    opponent = StringField('Opponent', validators=[DataRequired()])
    season = StringField('Season', validators=[DataRequired()])
    submit = SubmitField('Create Outing')

class PitchForm(FlaskForm):
    pitch_num = IntegerField('Pitch', validators=[DataRequired()])
    batter_id = StringField('Batter', validators=[DataRequired()])
    batter_hand = StringField('RHH/LHH', validators=[DataRequired()])
    velocity = IntegerField('Velo')
    lead_runner = IntegerField('Lean RNR')
    time_to_plate = DecimalField('Time to Plate')
    pitch_type = IntegerField('Pitch Type', validators=[DataRequired()])
    pitch_result = StringField('Pitch Result', validators=[DataRequired()])
    hit_spot = BooleanField('Hit Spot?', validators=[DataRequired()])
    count_balls = IntegerField('Balls', validators=[DataRequired()])
    count_strikes = IntegerField('Strikes', validators=[DataRequired()])
    result =  StringField('Result')
    fielder = IntegerField('Fielder')
    hit = BooleanField('Hit?')
    out = IntegerField('Outs')
    inning = IntegerField('Inning')
    submit = SubmitField('Finish Outing')
