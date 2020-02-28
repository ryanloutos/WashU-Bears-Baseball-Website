from app import db, login
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Boolean, index=True)
    retired = db.Column(db.Boolean, index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    # each user will have all their outings accessible through this

    def __repr__(self):
        return f'{self.firstname} {self.lastname}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Pitcher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    firstname = db.Column(db.String(64), index=True)
    lastname = db.Column(db.String(64), index=True)
    number = db.Column(db.Integer, index=True)
    notes = db.Column(db.String(1024), index=True)
    throws = db.Column(db.String(64), index=True)
    grad_year = db.Column(db.String(8), index=True)
    opponent_id = db.Column(db.Integer, db.ForeignKey('opponent.id'), index=True)
    retired = db.Column(db.Boolean, index=True)
    outings = db.relationship('Outing', backref='pitcher', lazy='dynamic')

    def __repr__(self):
        return self.name


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    opponent_id = db.Column(db.Integer,
                            db.ForeignKey('opponent.id'),
                            index=True)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), index=True)
    outings = db.relationship('Outing', backref='game', lazy='dynamic')

    def __repr__(self):
        return f"{self.date.month}/{self.date.day}/{self.date.year} vs. {self.opponent}"

    def get_season(self):
        return Season.query.filter_by(id=self.season_id).first()

    def get_opponent(self):
        opponent = Opponent.query.filter_by(id=self.opponent_id).first()
        return opponent

    def get_num_outings(self):
        count = 0
        for outing in self.outings:
            count += 1
        return count


class Outing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    opponent_id = db.Column(db.Integer,
                            db.ForeignKey('opponent.id'),
                            index=True)
    pitcher_id = db.Column(db.Integer, db.ForeignKey('pitcher.id'), index=True)
    # represents which pitcher this outing belongs to
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), index=True)
    at_bats = db.relationship('AtBat', backref='outing', lazy='dynamic')
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), index=True)
    # where all the pitches to the outing are stored

    def __repr__(self):
        year = self.date.year
        month = self.date.month
        day = self.date.day
        pitcher = Pitcher.query.filter_by(id=self.pitcher_id).first()

        return f'{month}/{day}/{year} - {pitcher} vs. {self.opponent}'

    def getDate(self):
        year = self.date.year
        month = self.date.month
        day = self.date.day
        return f"{month}/{year}"
    
    def getFullDate(self):
        year = self.date.year
        month = self.date.month
        day = self.date.day
        return f"{month}/{day}/{year}"

    def get_game(self):
        game = Game.query.filter_by(id=self.game_id).first()
        return game

    def get_pitcher(self):
        pitcher = Pitcher.query.filter_by(id=self.pitcher_id).first()
        return pitcher


class Pitch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    atbat_id = db.Column(db.Integer, db.ForeignKey('at_bat.id'), index=True)
    pitch_num = db.Column(db.Integer, index=True)
    batter_id = db.Column(db.Integer, db.ForeignKey('batter.id'), index=True)
    velocity = db.Column(db.Integer, index=True)
    lead_runner = db.Column(db.String(8), index=True)
    time_to_plate = db.Column(db.Float, index=True)
    pitch_type = db.Column(db.String(8), index=True)
    roll_through = db.Column(db.Boolean, index=True)
    short_set = db.Column(db.Boolean, index=True)
    pitch_result = db.Column(db.String(8), index=True)
    loc_x = db.Column(db.Float)
    loc_y = db.Column(db.Float)
    hit_spot = db.Column(db.Boolean, index=True)
    count = db.Column(db.String(8), index=True)
    ab_result = db.Column(db.String(32), index=True)
    traj = db.Column(db.String(8), index=True)
    fielder = db.Column(db.String(8), index=True)
    spray_x = db.Column(db.Float)
    spray_y = db.Column(db.Float)
    hit_hard = db.Column(db.Boolean, index=True)
    inning = db.Column(db.Integer, index=True)
    notes = db.Column(db.String(128))

    def __repr__(self):
        return f'<outing: {self.outing_id}, pitch: {self.pitch_num}>'

    def get_pitcher(self):
        at_bat = AtBat.query.filter_by(id=self.atbat_id).first()
        return at_bat.get_pitcher()

    def get_date(self):
        at_bat = AtBat.query.filter_by(id=self.atbat_id).first()
        return at_bat.get_date()


class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(8), index=True)
    year = db.Column(db.String(8), index=True)
    current_season = db.Column(db.Boolean, index=True)
    outings = db.relationship('Outing', backref='season', lazy='dynamic')
    videos = db.relationship('Video', backref='season', lazy='dynamic')
    games = db.relationship('Game', backref='season', lazy='dynamic')

    def __repr__(self):
        return f'{self.semester} {self.year}'


class Opponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    outings = db.relationship('Outing', backref='opponent', lazy='dynamic')
    batters = db.relationship('Batter', backref='opponent', lazy='dynamic', order_by="Batter.lastname")
    games = db.relationship('Game', backref='opponent', lazy='dynamic')

    def __repr__(self):
        return self.name


class Batter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    short_name = db.Column(db.String(8), index=True)
    number = db.Column(db.Integer, index=True)
    initials = db.Column(db.String(8), index=True)
    notes = db.Column(db.String(1024), index=True)
    bats = db.Column(db.String(8), index=True)
    grad_year = db.Column(db.String(8), index=True)
    opponent_id = db.Column(
        db.Integer,
        db.ForeignKey('opponent.id'),
        index=True)
    retired = db.Column(db.Boolean, index=True)
    at_bats = db.relationship('AtBat', backref='batter', lazy='dynamic')

    def __repr__(self):
        return self.short_name

    def name(self):
        return f"{self.firstname} {self.lastname}"

    def get_seasons(self):
        seasons = []
        for at_bat in self.at_bats:
            season = at_bat.get_season()
            if season not in seasons:
                seasons.append(season)
        return seasons

    def get_games(self):
        games = []
        for at_bat in self.at_bats:
            game = at_bat.get_game()
            if game not in games:
                games.append(game)
        return games

    def get_opponent(self):
        opponent = Opponent.query.filter_by(id=self.opponent_id).first()
        return opponent


class AtBat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batter_id = db.Column(db.Integer, db.ForeignKey('batter.id'), index=True)
    outing_id = db.Column(db.Integer, db.ForeignKey('outing.id'), index=True)
    pitches = db.relationship('Pitch', backref='at_bat', lazy='dynamic')

    def __repr__(self):
        outing = Outing.query.filter_by(id=self.outing_id).first()
        pitcher = User.query.filter_by(id=outing.pitcher_id).first()
        date = outing.date
        return f"{date} vs. {pitcher}"

    def get_num_pitches(self):
        count = 0
        for pitch in self.pitches:
            count += 1
        return count

    def get_pitcher(self):
        outing = Outing.query.filter_by(id=self.outing_id).first()
        pitcher = Pitcher.query.filter_by(id=outing.pitcher_id).first()
        return pitcher

    def get_batter(self):
        batter = Batter.query.filter_by(id=self.batter_id).first()
        return batter

    def get_date(self):
        outing = Outing.query.filter_by(id=self.outing_id).first()
        return outing.date

    def get_season(self):
        """Returns the season object for which this outing is in.

        Returns:
            [season object] -- [season object from models]
        """
        outing = Outing.query.filter_by(id=self.outing_id).first()
        season = Season.query.filter_by(id=self.outing.season_id).first()
        return season

    def get_game(self):
        outing = Outing.query.filter_by(id=self.outing_id).first()
        return outing.get_game()


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    date = db.Column(db.Date, index=True)
    pitcher_id = db.Column(db.Integer, db.ForeignKey('pitcher.id'), index=True)
    batter_id = db.Column(db.Integer, db.ForeignKey('batter.id'), index=True)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), index=True)
    outing_id = db.Column(db.Integer, db.ForeignKey('outing.id'), index=True)
    atbat_id = db.Column(db.Integer, db.ForeignKey('at_bat.id'), index=True)
    link = db.Column(db.String(128))

    def __repr__(self):
        return f"{self.date.month}/{self.date.day} - {self.title}"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
