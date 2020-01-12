from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db

from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat

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
