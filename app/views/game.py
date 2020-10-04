from app import db

from flask import flash
from flask import url_for
from flask import request
from flask import redirect
from flask import Blueprint
from flask import render_template

from flask_login import current_user
from flask_login import login_required

from app.forms import NewGameForm
from app.forms import EditGameForm

from app.models import Outing
from app.models import Pitch
from app.models import Season
from app.models import Opponent
from app.models import Batter
from app.models import Game
from app.models import Video

from app.stats.game_stats import game_hitting_stats
from app.stats.game_stats import game_pitching_stats

import os

game = Blueprint("game", __name__)


# ***************-WASHU PITCHING-*************** #
@game.route('/game/<id>/pitching', methods=['GET', 'POST'])
@login_required
def game_pitching(id):
    game = Game.query.filter_by(id=id).first()
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
    opponent_outings = Outing.query.filter_by(
        game_id=game.id, opponent_id=1).all()
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

    basic_stats_by_outing, basic_stats_game = game_pitching_stats(
        game, game.opponent_id)

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

    seasons = Season.query.order_by(Season.year).all()
    return render_template(
        "game/game_new_game.html",
        title="New Game",
        form=form,
        seasons=seasons
    )

# ***************-EDIT GAME-*************** #
@game.route("/edit_game/<id>", methods=["GET", "POST"])
@login_required
def edit_game(id):
    if not current_user.admin:
        flash('Admin feature only')
        return redirect(url_for('main.index'))

    game = Game.query.filter_by(id=id).first()
    if not game:
        flash("URL doesn't exist")
        redirect(url_for("main.index"))

    form = EditGameForm()
    print(form.opponent.data)
    if form.validate_on_submit():

        game.date = form.date.data
        game.opponent_id = form.opponent.data.id
        game.season_id = form.season.data.id

        db.session.commit()

        # redirects back to home page after outing was successfully created
        flash("Changes saved!")
        return redirect(url_for('game.game_pitching', id=game.id))

    outings = Outing.query.filter_by(game_id=id).all()
    can_edit_opponent = True
    if len(outings) > 0:
        can_edit_opponent = False

    seasons = Season.query.order_by(Season.year).all()
    opponents = Opponent.query.order_by(Opponent.name).all()
    file_loc = os.path.join(
        "images",
        "team_logos",
        f"{game.opponent.id}.png")

    return render_template(
        "game/edit_game.html",
        title="New Game",
        form=form,
        game=game,
        seasons=seasons,
        opponents=opponents,
        can_edit_opponent=can_edit_opponent,
        file_loc=file_loc
    )


# ***************-DELETE GAME-*************** #
@game.route("/delete_game/<id>", methods=["GET", "POST"])
@login_required
def delete_game(id):
    if not current_user.admin:
        flash('Admin feature only')
        return redirect(url_for('main.index'))

    game = Game.query.filter_by(id=id).first()
    if not game:
        flash("URL doesn't exist")
        redirect(url_for("main.index"))

    outings = Outing.query.filter_by(game_id=id).all()
    if len(outings) > 0:
        flash("Can't delete game because there are outings associated with it")
        return redirect(url_for('game.edit_game', id=id))

    videos = Video.query.filter_by(game_id=id).all()
    if len(videos) > 0:
        flash("Can't delete game because there are videos associated with it")
        return redirect(url_for('game.edit_game', id=id))

    db.session.delete(game)
    db.session.commit()

    flash('Game deleted!')
    return redirect(url_for('main.index'))
