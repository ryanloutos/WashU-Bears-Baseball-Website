from app import db

from flask import flash
from flask import url_for
from flask import request
from flask import redirect
from flask import Blueprint
from flask import render_template

from app.models import Season

from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

from werkzeug.urls import url_parse

other = Blueprint("other", __name__)


@other.context_processor
def template_variables():
    """Acts as the filler for main.html data. This will provide the seasons for the season selector.

    Returns:
        [dict] -- [contians season info for drop downs]
    """
    return dict(
        current_season=getCurrentSeason(),
        old_seasons=getOldSeasons())


@other.context_processor
def utility_functions():
    def truncate(n, decimals=2):
        """Truncates the passed value to decimal places.

        Arguments :
            n {number} -- Number to be truncated

        Keyword Arguments :
            decimals {int} -- Number of decimal places to truncate to(default : {2})

        Returns :
            [int]-- truncated verison of passed value
        """
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier
    return dict(
        truncate=truncate
    )


def getCurrentSeason():
    current_season = Season.query.filter_by(current_season=True).first()
    return current_season


def getOldSeasons():
    old_seasons = Season.query.filter_by(current_season=False).order_by(Season.year).all()
    return old_seasons
