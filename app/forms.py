from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, IntegerField, DecimalField, SelectField, FieldList, FormField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional
from app.models import User


# Basic form for users to login, must type in both username and a password
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# Creating a new account.
class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    year = RadioField('Year', choices=[('FR', 'FR'),('SO', 'SO'),('JR', 'JR'),('SR', 'SR')], validators=[DataRequired()])
    throws = RadioField('Throws', choices=[('R', 'R'),('L', 'L')], validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])  # Email() validator makes sure it's in email form
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(  # make sure passwords match
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

class PitchForm(FlaskForm):
    pitch_num = IntegerField('Pitch', validators=[DataRequired()])
    batter_id = StringField('Batter', validators=[DataRequired()])
    batter_hand = SelectField('RHH/LHH', choices=[('RHH','RHH'), ('LHH','LHH')], validators=[DataRequired()])
    velocity = IntegerField('Velo', validators=[Optional()])
    lead_runner = SelectField('Lead RNR', choices=[('Empty','Empty'), ('1','1'), ('2','2'), ('3','3')], validators=[DataRequired()])
    time_to_plate = DecimalField('Time to Plate', places=2, validators=[Optional()])
    pitch_type = SelectField('Pitch Type', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5'), ('7','7')], validators=[DataRequired()])
    pitch_result = SelectField('Pitch Result', choices=[('B','B'),('CS','CS'),('SS','SS'),('F','F'),('IP','IP')], validators=[DataRequired()])
    hit_spot = BooleanField('Hit Spot?', validators=[Optional()])
    count_balls = SelectField('Balls', choices=[('0','0'),('1','1'),('2','2'),('3','3')], validators=[DataRequired()])
    count_strikes = SelectField('Strikes', choices=[('0','0'),('1','1'),('2','2')], validators=[DataRequired()])
    result =  SelectField('Result', choices=[('',''),('GB','GB'),('FB','FB'),('LD','LD'),('K','K'),('KL','KL')], validators=[Optional()])
    fielder = SelectField('Fielder', choices=[('',''),('P','P'),('C','C'),('1B','1B'),('2B','2B'),('3B','3B'),('SS','SS'),('LF','LF'),('CF','CF'),('RF','RF')], validators=[Optional()])
    hit = BooleanField('Hit?', validators=[Optional()])
    out = SelectField('Out #', choices=[('',''),('1','1'),('2','2'),('3','3')], validators=[Optional()])
    inning = IntegerField('Inning', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        FlaskForm.__init__(self, *args, **kwargs)

# Creating a new outing
class OutingForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    opponent = StringField('Opponent', validators=[DataRequired()])
    season = StringField('Season', validators=[DataRequired()])
    pitch = FieldList(FormField(PitchForm), min_entries=1, max_entries=150, validators=[DataRequired()])
    submit = SubmitField('Create Outing')


# class AllPitchForm(FlaskForm):
#     pitch = FieldList(FormField(PitchForm), min_entries=1, max_entries=150, validators=[DataRequired()])
#     submit = SubmitField("Finish Outing")
