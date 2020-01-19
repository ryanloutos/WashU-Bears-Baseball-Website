from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import RadioField, IntegerField, DecimalField, SelectField
from wtforms import FieldList, FormField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email
from wtforms.validators import EqualTo, Optional
from .models import User, Season, Opponent, Pitcher
from wtforms.ext.sqlalchemy.fields import QuerySelectField

# Basic form for users to login, must type in both username and a password
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# Creating a new season
class SeasonForm(FlaskForm):
    semester = SelectField(
        'Semester',
        choices=[('Fall', 'Fall'), ('Spring', 'Spring')],
        validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    current_season = BooleanField('Current Season?')
    submit = SubmitField('Create New Season')


# Creating a new batter
class BatterForm(FlaskForm):
    fullname = StringField('Name', validators=[Optional()])
    nickname = StringField('Initials/Number', validators=[Optional()])
    bats = SelectField(
        'Bats',
        choices=[('R', 'R'), ('L', 'L'), ('S', 'S')],
        validators=[Optional()])
    grad_year = StringField('Grad Year', validators=[Optional()])
    retired = BooleanField('Retired?')
    submit = SubmitField('Create Batter', validators=[Optional()])


# Creating a new batter
class NewBatterForm(FlaskForm):
    opponent = SelectField('Opponent', validators=[Optional()])
    fullname = StringField('Name', validators=[Optional()])
    nickname = StringField('Initials/Number', validators=[Optional()])
    bats = SelectField(
        'Bats',
        choices=[('R', 'R'), ('L', 'L'), ('S', 'S')],
        validators=[Optional()])
    grad_year = StringField('Grad Year', validators=[Optional()])
    retired = BooleanField('Retired?')
    submit = SubmitField('Create Batter', validators=[Optional()])


class EditBatterForm(FlaskForm):
    opponent = SelectField('Opponent', validators=[Optional()])
    fullname = StringField('Name', validators=[Optional()])
    nickname = StringField('Initials/Number', validators=[Optional()])
    bats = SelectField(
        'Bats',
        choices=[('R', 'R'), ('L', 'L'), ('S', 'S')],
        validators=[Optional()])
    grad_year = StringField('Grad Year', validators=[Optional()])
    retired = BooleanField('Retired?')
    submit = SubmitField('Save Changes', validators=[Optional()])

# Creating a new opponent
class OpponentForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired()])
    batter = FieldList(
        FormField(BatterForm),
        min_entries=2,
        max_entries=50,
        validators=[Optional()]
    )
    submit = SubmitField('Create New Opponent')


class EditOpponentForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired()])
    file = FileField(
        'Team Logo',
        validators=[FileRequired()]   
    )
    submit = SubmitField('Save Changes')


# Creating a new account. Only admin users can access this page
class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Email() validator makes sure it's in email form
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(  # make sure passwords match
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    admin = BooleanField('Admin?', validators=[Optional()])
    retired = BooleanField('Retired?', validators=[Optional()])
    submit = SubmitField('Register')

    # these two functions will run automatically when a new user is trying to
    def validate_username(self, username):
        '''Be created make sure username doesn't already exist in database'''
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        '''Make sure email doesn't already exist in database'''
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Changes')

    def validate_username(self, username):
        '''Be created make sure username doesn't already exist in database'''
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        '''Make sure email doesn't already exist in database'''
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(  # make sure passwords match
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')
    

# each field is based on the baseball teams velocity tracking sheets
class PitchForm(FlaskForm):
    batter_id = SelectField('Batter', validators=[Optional()])
    velocity = IntegerField('Velo', validators=[Optional()])
    lead_runner = SelectField(
        'Lead RNR',
        choices=[('', ''), ('1', '1'), ('2', '2'), ('3', '3')],
        validators=[Optional()])
    time_to_plate = DecimalField(
        'Time to Plate',
        places=2,
        validators=[Optional()])
    pitch_type = SelectField(
        'Pitch Type',
        choices=[
            ('1', '1'), ('2', '2'), ('3', '3'),
            ('4', '4'), ('5', '5'), ('7', '7')],
        validators=[Optional()])
    pitch_result = SelectField(
        'Pitch Result',
        choices=[
            ('B', 'B'), ('CS', 'CS'), ('SS', 'SS'),
            ('F', 'F'), ('IP', 'IP')],
        validators=[Optional()])
    hit_spot = BooleanField('Hit Spot?', validators=[Optional()])
    ab_result = SelectField(
        'Result',
        choices=[
            ('', ''), ('IP->Out', 'IP->Out'), ('K', 'K'),
            ('KL', 'KL'), ('BB', 'BB'), ('HBP', 'HBP'),
            ('1B', '1B'), ('2B', '2B'), ('3B', '3B'),
            ('HR', 'HR'), ('Error', 'Error'), ('CI', 'CI'), ('FC', 'FC'),
            ('D3->Out', 'D3->Out'),
            ('D3->Safe', 'D3->Safe'),
            ('Other', 'Other')],
        validators=[Optional()])
    traj = SelectField(
        'GB/LD/FB',
        choices=[('', ''), ('GB', 'GB'), ('LD', 'LD'), ('FB', 'FB')],
        validators=[Optional()])
    fielder = SelectField(
        'Fielder',
        choices=[
            ('', ''), ('1', '1'), ('2', '2'), ('3', '3'),
            ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
            ('8', '8'), ('9', '9')],
        validators=[Optional()])
    inning = IntegerField('Inning', validators=[Optional()])
    submit = SubmitField('Finish', validators=[Optional()])

    # disables CSRF tokens for subforms, but keeps it for the big
    # form (OutingForm) so it is still secured
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        FlaskForm.__init__(self, *args, **kwargs)


# Fieldlist to input all pitches in an outing
class OutingPitchForm(FlaskForm):
    pitch = FieldList(
        FormField(PitchForm),
        min_entries=1,
        max_entries=150,
        validators=[Optional()])
    submit = SubmitField('Add Pitches')


# Creating a new outing
class OutingForm(FlaskForm):
    pitcher = SelectField('Pitcher', validators=[Optional()])
    date = DateField('Date', validators=[Optional()], format='%Y-%m-%d')
    opponent = QuerySelectField(
        query_factory=lambda: Opponent.query,
        get_pk=lambda o: o,
        get_label=lambda o: o)
    season = QuerySelectField(
        query_factory=lambda: Season.query,
        get_pk=lambda s: s,
        get_label=lambda s: s)
    submit = SubmitField('Create Outing')


# Create a new outing from CSV
class NewOutingFromCSV(FlaskForm):
    """Class for the html form for making an outing from a CSV.

    Arguments:
        FlaskForm {[FlaskFrom]} -- [inheritance of form]

    Fields:
        file {file} -- csv file to be parsed with outing information
    """
    pitcher = SelectField('Pitcher', validators=[Optional()])
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    opponent = QuerySelectField(
        query_factory=lambda: Opponent.query,
        get_pk=lambda o: o,
        get_label=lambda o: o)
    season = QuerySelectField(
        query_factory=lambda: Season.query,
        get_pk=lambda s: s,
        get_label=lambda s: s)
    file = FileField(
        'Outing File',
        validators=[FileRequired()]
        # validators.regexp('([a-zA-Z0-9\s_\\.\-\(\):])+(.csv)$')
        )

    submit = SubmitField('Validate Outing')


class NewOutingFromCSVPitches(FlaskForm):
    pitch = FieldList(
        FormField(PitchForm),
        min_entries=1,
        max_entries=150,
        validators=[Optional()])
    submit = SubmitField('Create Outing')
