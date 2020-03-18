from flask import Blueprint
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db

from app.forms import NewSeasonForm, EditSeasonForm
from app.models import Outing, Pitch, Season, AtBat, Game, Video

season = Blueprint("season", __name__)

# ***************-SEASON HOMEPAGE-*************** #
@season.route("/season/<id>")
@login_required
def season_home(id):
    # get the season object trying to be viewed and redirect if doesn't exist
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
    # if user is not an admin, they can't create a new season
    if not current_user.admin:
        flash("You are not an admin and cannot create a season")
        return redirect(url_for("main.index"))

    # if the form is validated, add season to db
    form = NewSeasonForm()
    if form.validate_on_submit():
        season = Season(
            semester=form.semester.data,
            year=form.year.data,
            current_season=form.current_season.data
        )
        db.session.add(season)
        db.session.commit()

        flash("New season created!")
        return redirect(url_for("season_home", id=season.id))

    return render_template(
        "season/new_season.html",
        title="New Season",
        form=form
    )

# ***************-EDIT SEASON-*************** #
@season.route("/edit_season/<id>", methods=["GET", "POST"])
@login_required
def edit_season(id):
    # if user is not an admin, they can't create a new season
    if not current_user.admin:
        flash("You are not an admin and cannot edit a season")
        return redirect(url_for("main.index"))

    # get the season object trying to be edited and redirect if doesn't exist
    season = Season.query.filter_by(id=id).first()
    if not season:
        flash("URL does not exist")
        return redirect(url_for("main.index"))

    # once the user clicks Save Changes, make the changes to the Season in db
    form = EditSeasonForm()
    if form.validate_on_submit():

        # if this season become the current season
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
@season.route("/delete_season/<id>/<everything>", methods=["GET", "POST"])
@login_required
def delete_season(id, everything):
    # if user is not an admin, they can't delete a season
    if not current_user.admin:
        flash("You are not an admin and cannot edit a season")
        return redirect(url_for("main.index"))

    season_to_delete = Season.query.filter_by(id=id).first_or_404()
    
    # means that all videos, outings, and games will be deleted
    if everything == "yes":
        videos = Video.query.filter_by(season_id=id).all()
        for video in videos:
            db.session.delete(video)
        
        games = Game.query.filter_by(season_id=id).all()
        for game in games:
            db.session.delete(game)
        
        outings = Outing.query.filter_by(season_id=id).all()
        for outing in outings:
            for at_bat in outing.at_bats:
                for pitch in at_bat.pitches:
                    db.session.delete(pitch)
                db.session.delete(at_bat)
            db.session.delete(outing)

        db.session.delete(season_to_delete)
        db.session.commit()

    # will only the delete the season itself and changed the foreign keys to none
    elif everything == "no":
        videos = Video.query.filter_by(season_id=id).all()
        for video in videos:
            video.season_id = None
        
        games = Game.query.filter_by(season_id=id).all()
        for game in games:
            game.season_id = None
        
        outings = Outing.query.filter_by(season_id=id).all()
        for outing in outings:
            outing.season_id = None

        db.session.delete(season_to_delete)
        db.session.commit()
    
    # if something else is sent through the url
    else: 
        return redirect(url_for("season.edit_season", id=id))

    return redirect(url_for("main.index"))