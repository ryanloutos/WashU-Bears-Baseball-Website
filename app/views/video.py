from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.forms import NewOutingFromCSV, SeasonForm, OpponentForm, BatterForm
from app.forms import OutingPitchForm, NewOutingFromCSVPitches, EditUserForm
from app.forms import ChangePasswordForm, EditBatterForm, EditOpponentForm
from app.forms import NewBatterForm, NewGameForm, PitcherNewVideoForm, BatterNewVideoForm
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat, Game, Video
from app.stats import calcPitchPercentages, pitchUsageByCount, calcAverageVelo
from app.stats import calcPitchStrikePercentage, calcPitchWhiffRate
from app.stats import createPitchPercentagePieChart, velocityOverTimeLineChart
from app.stats import pitchStrikePercentageBarChart, avgPitchVeloPitcher
from app.stats import pitchUsageByCountLineCharts, pitchStrikePercentageSeason
from app.stats import pitchUsageSeason, seasonStatLine, staffBasicStats
from app.stats import staffPitcherAvgVelo, staffPitchStrikePercentage
from app.stats import outingPitchStatistics, outingTimeToPlate, veloOverTime
from app.stats import teamImportantStatsSeason, gameBasicStatsByOuting, game_opponent_stats_calc

# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random


video = Blueprint("video", __name__)

# ***************-NEW VIDEO PITCHER-*************** #
@video.route('/new_video_pitcher', methods=['GET', 'POST'])
@login_required
def new_video_pitcher():
    form = PitcherNewVideoForm()

    current_season = Season.query.filter_by(current_season=1).first()

    if form.validate_on_submit():

        if form.outing.data is None:
            outing_id = ""
        else:
            outing_id = form.outing.data.id

        video = Video(
            title=form.title.data,
            date=form.date.data,
            season_id=form.season.data.id,
            outing_id=outing_id,
            pitcher_id=form.pitcher.data.id,
            link=form.link.data
        )

        db.session.add(video)
        db.session.commit()

        flash("Video Posted!")
        return redirect(url_for("main.index")) 
    
    return render_template(
        "video/new_video_pitcher.html",
        title="Post Video",
        form=form,
        current_season=current_season
    )

# ***************-NEW VIDEO BATTER-*************** #
@video.route('/new_video_batter', methods=['GET', 'POST'])
@login_required
def new_video_batter():
    form = BatterNewVideoForm()

    current_season = Season.query.filter_by(current_season=1).first()

    batters = []
    for b in Batter.query.filter_by(opponent_id=1).filter_by(retired=0).all():
        batters.append((str(b.id),f"{b.firstname} {b.lastname}"))
    form.batter.choices = batters

    if form.validate_on_submit():

        video = Video(
            title=form.title.data,
            date=form.date.data,
            season_id=form.season.data.id,
            batter_id=form.batter.data,
            link=form.link.data
        )

        db.session.add(video)
        db.session.commit()

        flash("Video Posted!")
        return redirect(url_for("main.index")) 
    
    return render_template(
        "video/new_video_batter.html",
        title="Post Video",
        form=form,
        current_season=current_season
    )
    