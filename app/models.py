from app import db, login
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# Setting up User table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Boolean, index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    year = db.Column(db.String(32), index=True)
    throws = db.Column(db.String(8), index=True)
    outings = db.relationship('Outing', backref='pitcher', lazy='dynamic')
    # each user will have all their outings accessible through this

    def __repr__(self):
        return f'{self.firstname} {self.lastname}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Setting up Outing table
class Outing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    opponent = db.Column(db.String(32), index=True)
    season = db.Column(db.String(32), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    # represents which pitcher this outing belongs to
    pitches = db.relationship('Pitch', backref='outing', lazy='dynamic')
    # where all the pitches to the outing are stored

    def __repr__(self):
        year = self.date.year
        month = self.date.month
        day = self.date.day
        return f'{month}/{day} {self.opponent}'

    def get_id(self):
        return self.id


# Sets up Pitch table
class Pitch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    outing_id = db.Column(db.Integer, db.ForeignKey('outing.id'), index=True)
    # which outing this pitch comes from
    pitch_num = db.Column(db.Integer, index=True)
    batter_id = db.Column(db.String(16), index=True)
    batter_hand = db.Column(db.String(8), index=True)
    velocity = db.Column(db.Integer, index=True)
    lead_runner = db.Column(db.String(8), index=True)
    time_to_plate = db.Column(db.Float, index=True)
    pitch_type = db.Column(db.String(8), index=True)
    pitch_result = db.Column(db.String(8), index=True)
    hit_spot = db.Column(db.Boolean, index=True)
    count_balls = db.Column(db.String(8), index=True)
    count_strikes = db.Column(db.String(8), index=True)
    result = db.Column(db.String(8), index=True)
    fielder = db.Column(db.String(8), index=True)
    hit = db.Column(db.Boolean, index=True)
    out = db.Column(db.String(8), index=True)
    inning = db.Column(db.Integer, index=True)

    def __repr__(self):
        return f'<outing: {self.outing_id}, pitch: {self.pitch_num}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
