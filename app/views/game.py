from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.forms import NewOutingFromCSV, SeasonForm, OpponentForm, BatterForm
from app.forms import OutingPitchForm, NewOutingFromCSVPitches, EditUserForm
from app.forms import ChangePasswordForm, EditBatterForm, EditOpponentForm
from app.forms import NewBatterForm, NewGameForm
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat, Game
from app.stats import calcPitchPercentages, pitchUsageByCount, calcAverageVelo
from app.stats import calcPitchStrikePercentage, calcPitchWhiffRate
from app.stats import createPitchPercentagePieChart, velocityOverTimeLineChart
from app.stats import pitchStrikePercentageBarChart, avgPitchVeloPitcher
from app.stats import pitchUsageByCountLineCharts, pitchStrikePercentageSeason
from app.stats import pitchUsageSeason, seasonStatLine, staffBasicStats
from app.stats import staffPitchStrikePercentage
from app.stats import outingPitchStatistics, outingTimeToPlate, veloOverTime
from app.stats import teamImportantStatsSeason, gameBasicStatsByOuting, game_opponent_stats_calc

# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random


game = Blueprint("game", __name__)

# ***************-GAME HOMEPAGE-*************** #
@game.route('/game/<id>', methods=['GET', 'POST'])
@login_required
def game_outings(id):

    # get the game object assicated with the id
    game = Game.query.filter_by(id=id).first()

    if not game:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    basic_stats_by_outing, basic_stats_game = gameBasicStatsByOuting(game)

    file_loc = os.path.join("images",
                            "team_logos",
                            f"{game.opponent.id}.png")

    # bug or user trying to view opponent that DNE
    if not game:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template('game/game_outings.html',
                           title=game,
                           game=game,
                           basic_stats_by_outing=basic_stats_by_outing,
                           basic_stats_game=basic_stats_game,
                           file_loc=file_loc)


@game.route("/game/<id>/opponent_stats", methods=['GET', 'POST'])
@login_required
def game_opponent_stats(id):

    game = Game.query.filter_by(id=id).first()

    # if game id is not correct, let them know and send them home
    if not game:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    game_stats = game_opponent_stats_calc(game)

    # setup opponent logo file
    file_loc = os.path.join(
        "images",
        "team_logos",
        f"{game.opponent.id}.png")

    return render_template(
        'game/game_opponent_stats.html',
        title=game,
        game=game,
        file_loc=file_loc,
        game_opponent_stats=game_stats
    )


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
