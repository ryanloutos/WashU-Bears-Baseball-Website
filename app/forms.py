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


# Creating a new account. Only admin users can access this page
class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    year = RadioField('Year/Position', choices=[('FR', 'FR'),('SO', 'SO'),('JR', 'JR'),('SR', 'SR'),('Coach/Manager','Coach/Manager')], validators=[DataRequired()])
    throws = RadioField('Throws', choices=[('R', 'R'),('L', 'L')], validators=[Optional()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])  # Email() validator makes sure it's in email form
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(  # make sure passwords match
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    admin = BooleanField('Admin?', validators=[Optional()])
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

#each field is based on the baseball teams velocity tracking sheets
class PitchForm(FlaskForm):
    pitch_num = IntegerField('Pitch', validators=[DataRequired()])
    batter_id = StringField('Batter', validators=[DataRequired()])
    batter_hand = SelectField('RHH/LHH', choices=[('','Select'),('RHH','RHH'), ('LHH','LHH')], validators=[DataRequired()])
    velocity = IntegerField('Velo', validators=[Optional()])
    lead_runner = SelectField('Lead RNR', choices=[('Empty','Empty'), ('1','1'), ('2','2'), ('3','3')], validators=[Optional()])
    time_to_plate = DecimalField('Time to Plate', places=2, validators=[Optional()])
    pitch_type = SelectField('Pitch Type', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5'), ('7','7')], validators=[Optional()])
    pitch_result = SelectField('Pitch Result', choices=[('B','B'),('CS','CS'),('SS','SS'),('F','F'),('IP','IP')], validators=[Optional()])
    hit_spot = BooleanField('Hit Spot?', validators=[Optional()])
    count_balls = SelectField('Balls', choices=[('0','0'),('1','1'),('2','2'),('3','3')], validators=[Optional()])
    count_strikes = SelectField('Strikes', choices=[('0','0'),('1','1'),('2','2')], validators=[Optional()])
    result =  SelectField('Result', choices=[('','Select'),('GB','GB'),('FB','FB'),('LD','LD'),('K','K'),('KL','KL'),('BB','BB'),('HBP','HBP')], validators=[Optional()])
    fielder = SelectField('Fielder', choices=[('','Select'),('P','P'),('C','C'),('1B','1B'),('2B','2B'),('3B','3B'),('SS','SS'),('LF','LF'),('CF','CF'),('RF','RF')], validators=[Optional()])
    hit = BooleanField('Hit?', validators=[Optional()])
    out = SelectField('Out #', choices=[('','Select'),('1','1'),('2','2'),('3','3')], validators=[Optional()])
    inning = IntegerField('Inning', validators=[Optional()])

    #disables CSRF tokens for subforms, but keeps it for the big form (OutingForm) so it is still secured
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        FlaskForm.__init__(self, *args, **kwargs)

# Creating a new outing
class OutingForm(FlaskForm):
    pitcher = SelectField('Pitcher', validators=[Optional()])
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    opponent = StringField('Opponent', validators=[DataRequired()])
    season = StringField('Season', validators=[DataRequired()])
    pitch = FieldList(FormField(PitchForm), min_entries=1, max_entries=150, validators=[DataRequired()])
    submit = SubmitField('Create Outing')\