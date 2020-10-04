from app import db

from flask import Blueprint
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for

from flask_login import current_user
from flask_login import login_required

from app.forms import NewSeasonForm
from app.forms import EditSeasonForm

from app.models import Outing
from app.models import Pitch
from app.models import Season
from app.models import AtBat
from app.models import Game
from app.models import Video

season = Blueprint("season", __name__)


# ***************-SEASON HOMEPAGE-*************** #
@season.route("/season/<id>")
@login_required
def season_home(id):
    season = Season.query.filter_by(id=id).first()
    if not season:
        flash("URL does not exist")
        return redirect(url_for("main.index"))

    games = Game.query.filter_by(season_id=id).order_by(Game.date).all()

    return render_template(
        "season/season.html",
        title=season,
        games=games,
        season=season
    )


# ***************-NEW SEASON-*************** #
@season.route("/new_season", methods=["GET", "POST"])
@login_required
def new_season():
    if not current_user.admin:
        flash("You are not an admin and cannot create a season")
        return redirect(url_for("main.index"))

    form = NewSeasonForm()
    if form.validate_on_submit():

        if form.current_season.data:
            seasons = Season.query.all()
            for s in seasons:
                s.current_season = False

        season = Season(
            semester=form.semester.data,
            year=form.year.data,
            current_season=form.current_season.data
        )

        db.session.add(season)
        db.session.commit()

        flash("New season created!")
        return redirect(url_for("season.season_home", id=season.id))

    return render_template(
        "season/new_season.html",
        title="New Season",
        form=form
    )


# ***************-EDIT SEASON-*************** #
@season.route("/edit_season/<id>", methods=["GET", "POST"])
@login_required
def edit_season(id):
    if not current_user.admin:
        flash("You are not an admin and cannot edit a season")
        return redirect(url_for("main.index"))

    season = Season.query.filter_by(id=id).first()
    if not season:
        flash("URL does not exist")
        return redirect(url_for("main.index"))

    form = EditSeasonForm()
    if form.validate_on_submit():

        if form.current_season.data:
            seasons = Season.query.all()
            for s in seasons:
                s.current_season = False

        season.semester = form.semester.data
        season.year = form.year.data
        season.current_season = form.current_season.data

        db.session.commit()

        flash("Changes made!")
        return redirect(url_for("season.season_home", id=id))

    return render_template(
        "season/edit_season.html",
        title="New Season",
        season=season,
        form=form
    )


# ***************-DELETE SEASON-*************** #
@season.route("/delete_season/<id>", methods=["GET", "POST"])
@login_required
def delete_season(id):
    if not current_user.admin:
        flash("You are not an admin and cannot edit a season")
        return redirect(url_for("main.index"))

    season = Season.query.filter_by(id=id).first()
    if not season:
        flash("Can't delete a season that doesn't exist")
        return redirect(url_for('main.index'))

    games = Game.query.filter_by(season_id=id).all()
    if len(games) > 0:
        flash("Can't delete the season because there are games associated with it")
        return redirect(url_for('season.season_home', id=id))

    outings = Outing.query.filter_by(season_id=id).all()
    if len(outings) > 0:
        flash("Can't delete the season because there are outings associated with it")
        return redirect(url_for('season.season_home', id=id))

    videos = Video.query.filter_by(season_id=id).all()
    if len(videos) > 0:
        flash("Can't delete the season because there are videos associated with it")
        return redirect(url_for('season.season_home', id=id))

    db.session.delete(season)
    db.session.commit()

    flash("Season deleted!")
    return redirect(url_for("main.index"))
