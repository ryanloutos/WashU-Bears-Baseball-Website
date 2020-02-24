from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.forms import NewGameForm
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat, Game
from app.stats import game_pitching_stats, game_hitting_stats

# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random


game = Blueprint("game", __name__)


# ***************-WASHU PITCHING-*************** #
@game.route('/game/<id>/pitching', methods=['GET', 'POST'])
@login_required
def game_pitching(id):

    game = Game.query.filter_by(id=id).first()
    if not game:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    if not game:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    basic_stats_by_outing, basic_stats_game = game_pitching_stats(game, 1)

    file_loc = os.path.join(
        "images",
        "team_logos",
        f"{game.opponent.id}.png")

    return render_template(
        'game/game_pitching.html',
        title=game,
        game=game,
        file_loc=file_loc,
        basic_stats_by_outing=basic_stats_by_outing,
        basic_stats_game=basic_stats_game
    )


# ***************-WASHU HITTING-*************** #
@game.route("/game/<id>/hitting", methods=['GET', 'POST'])
@login_required
def game_hitting(id):

    game = Game.query.filter_by(id=id).first()

    if not game:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    game_stats = game_hitting_stats(game, 1)

    file_loc = os.path.join(
        "images",
        "team_logos",
        f"{game.opponent.id}.png"
    )

    # Get all pitches in the game vs our hitters
    opponent_outings = Outing.query.filter_by(game_id=game.id, opponent_id=game.opponent_id).all()
    pitches = []
    for outing in opponent_outings:
        pitcher = outing.get_pitcher()
        for ab in outing.at_bats:
            batter = ab.get_batter()
            for p in ab.pitches:
                pitches.append({
                    "pitch_type": p.pitch_type,
                    "x": p.loc_x,
                    "y": p.loc_y,
                    "pitcher_hand": pitcher.throws,
                    "batter_hand": batter.bats
                })

    return render_template(
        'game/game_hitting.html',
        title=game,
        game=game,
        file_loc=file_loc,
        game_opponent_stats=game_stats,
        pitches=pitches
    )


# ***************-OPPONENT PITCHING-*************** #
@game.route("/game/<id>/opponent/pitching", methods=["GET", "POST"])
@login_required
def game_opponent_pitching(id):

    game = Game.query.filter_by(id=id).first()
    if not game:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    basic_stats_by_outing, basic_stats_game = game_pitching_stats(game, game.opponent_id)

    file_loc = os.path.join(
        "images",
        "team_logos",
        f"{game.opponent.id}.png"
    )

    return render_template(
        'game/game_opponent_pitching.html',
        title=game,
        game=game,
        file_loc=file_loc,
        basic_stats_by_outing=basic_stats_by_outing,
        basic_stats_game=basic_stats_game
    )


# ***************-OPPONENT HITTING-*************** #
@game.route("/game/<id>/opponent/hitting", methods=["GET", "POST"])
@login_required
def game_opponent_hitting(id):

    game = Game.query.filter_by(id=id).first()
    if not game:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    game_stats = game_hitting_stats(game, game.opponent_id)

    file_loc = os.path.join(
        "images",
        "team_logos",
        f"{game.opponent.id}.png")

    return render_template(
        'game/game_opponent_hitting.html',
        title=game,
        game=game,
        file_loc=file_loc,
        game_opponent_stats=game_stats
    )


# ***************-NEW GAME-*************** #
@game.route("/game/new_game", methods=["GET", "POST"])
@login_required
def game_new_game():
    form = NewGameForm()

    if form.validate_on_submit():
        new_game = Game(
            date=form.date.data,
            opponent_id=form.opponent.data.id,
            season_id=form.season.data.id
        )
        db.session.add(new_game)
        db.session.commit()

        # redirects back to home page after outing was successfully created
        flash("New Game Created!")
        return redirect(url_for('main.index'))

    return render_template(
        "game/game_new_game.html",
        form=form
    )
