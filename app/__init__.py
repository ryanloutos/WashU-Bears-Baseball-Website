from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

# setting up necessary variables, packages, etc on entry
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'main.login'
bootstrap = Bootstrap(app)

# this position is required for flask to function
from app import routes, models, errors

# import blueprints
from .views.main import main
from .views.staff import staff
from .views.pitcher import pitcher
from .views.outing import outing
from .views.batter import batter
from .views.opponent import opponent
from .views.season import season
from .views.other import other
from .views.api import api
from .views.game import game

# Register Blueprints
app.register_blueprint(main)
app.register_blueprint(staff)
app.register_blueprint(pitcher)
app.register_blueprint(outing)
app.register_blueprint(batter)
app.register_blueprint(opponent)
app.register_blueprint(season)
app.register_blueprint(other)
app.register_blueprint(api)
app.register_blueprint(game)
