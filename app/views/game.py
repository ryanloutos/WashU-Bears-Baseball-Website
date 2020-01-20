from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.forms import NewOutingFromCSV, SeasonForm, OpponentForm, BatterForm
from app.forms import OutingPitchForm, NewOutingFromCSVPitches, EditUserForm
from app.forms import ChangePasswordForm, EditBatterForm, EditOpponentForm
from app.forms import NewBatterForm
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat, Game
from app.stats import calcPitchPercentages, pitchUsageByCount, calcAverageVelo
from app.stats import calcPitchStrikePercentage, calcPitchWhiffRate
from app.stats import createPitchPercentagePieChart, velocityOverTimeLineChart
from app.stats import pitchStrikePercentageBarChart, avgPitchVeloPitcher
from app.stats import pitchUsageByCountLineCharts, pitchStrikePercentageSeason
from app.stats import pitchUsageSeason, seasonStatLine, staffBasicStats
from app.stats import staffPitcherAvgVelo, staffPitchStrikePercentage
from app.stats import outingPitchStatistics, outingTimeToPlate, veloOverTime
from app.stats import teamImportantStatsSeason, gameBasicStatsByOuting

# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random


game = Blueprint("game", __name__)

# ***************-GAME HOMEPAGE-*************** #
@game.route('/game/<id>', methods=['GET','POST'])
@login_required
def game_outings(id):

    # get the game object assicated with the id
    game = Game.query.filter_by(id=id).first()

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