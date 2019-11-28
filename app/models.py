from app import db, login
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    year = db.Column(db.String(8))
    throws = db.Column(db.String(8))
    outings = db.relationship('Outing', backref='pitcher', lazy='dynamic')

    def __repr__(self):
        return '{} {}'.format(self.firstname, self.lastname) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Outing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    opponent = db.Column(db.String(32), index=True)
    season = db.Column(db.String(32), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

    def __repr__(self):
        year = self.date.year
        month = self.date.month
        day = self.date.day
        return '{}/{} {}'.format(month, day, self.opponent)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
