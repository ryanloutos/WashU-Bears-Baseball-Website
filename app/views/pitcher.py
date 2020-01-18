from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db

from app.models import User, Outing, Pitch, Season, Pitcher
from app.stats import avgPitchVeloPitcher
from app.stats import pitchStrikePercentageSeason
from app.stats import pitchUsageSeason, seasonStatLine

# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random

pitcher = Blueprint("pitcher", __name__)

# ***************-PITCHER HOMEPAGE-*************** # DONE
@pitcher.route('/pitcher/<id>', methods=['GET', 'POST'])
@login_required
def pitcher_home(id):
    '''
    PITCHER HOMEPAGE:
    Displays different pages related to a specific pitcher

    PARAM:
        -id: the id (primary key) of the pitcher that wants
            to be viewed

    RETURN:
        -pitcher_home.html which has "quick hitter" info
            and can navigate to other pages using side nav
    '''
    # get the user object associated with the id in the url
    pitcher = Pitcher.query.filter_by(id=id).first()

    # either bug or user trying to access pitcher page that DNE
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    # get the outings associated with that player
    outings = pitcher.outings

    # get the number of outings they have thrown
    num_outings = 0
    for o in outings:
        num_outings += 1

    # set the 3 most recent outings thrown by pitcher
    if num_outings >= 3:
        recent_outings = [outings[i] for i in range(3)]
        for outing in outings:
            if outing.date >= recent_outings[2].date:
                if outing.date >= recent_outings[1].date:
                    if outing.date >= recent_outings[0].date:
                        recent_outings[2] = recent_outings[1]
                        recent_outings[1] = recent_outings[0]
                        recent_outings[0] = outing
                    else:
                        recent_outings[2] = recent_outings[1]
                        recent_outings[1] = outing
                else:
                    recent_outings[2] = outing
    else:
        recent_outings = [outings[i] for i in range(num_outings)]

    return render_template('pitcher/pitcher_home.html',
                           title=pitcher,
                           pitcher=pitcher,
                           recent_outings=recent_outings)

# ***************-PITCHER OUTINGS-*************** #
@pitcher.route('/pitcher/<id>/outings', methods=['GET', 'POST'])
@login_required
def pitcher_outings(id):
    '''
    PITCHER OUTINGS:
    Displays the outings thrown by a pitcher

    PARAM:
        -id: the id (primary key) of the pitcher that wants
            to be viewed

    RETURN:
        -pitcher_outings.html which holds a table showing all
            of their outings
    '''
    # get the user object associated with the username in the url
    pitcher = Pitcher.query.filter_by(id=id).first()

    # either bug or user trying to access pitcher page that DNE
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    # get the outings associated with that player
    outings = pitcher.outings

    # get seasons associated with player
    seasons = []
    for outing in outings:
        if outing.season not in seasons:
            seasons.append(outing.season)

    return render_template('pitcher/pitcher_outings.html',
                           title=pitcher,
                           pitcher=pitcher,
                           seasons=seasons)

# ***************-PITCHER BASIC STATS-*************** #
@pitcher.route('/pitcher/<id>/stats/basic', methods=['GET', 'POST'])
@login_required
def pitcher_stats_basic(id):
    '''
    PITCHER BASIC STATS:
    Displays basic game/outing statistics

    PARAM:
        -id: the id (primary key) of the pitcher that wants
            to be viewed

    RETURN:
        -pitcher_stats_basic.html which holds a table holding
            basic statistics
    '''

    # get the user object associated with the username in the url
    pitcher = Pitcher.query.filter_by(id=id).first()

    # either bug or user trying to access pitcher page that DNE
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    # get the outings associated with that player
    outings = pitcher.outings

    # get seasons associated with player
    seasons = []
    for outing in outings:
        if outing.season not in seasons:
            seasons.append(outing.season)

    # gets stats associated with pitcher
    season_stat_line, outing_stat_line = seasonStatLine(pitcher)

    return render_template('pitcher/pitcher_stats_basic.html',
                           title=pitcher,
                           pitcher=pitcher,
                           seasons=seasons,
                           season_stat_line=season_stat_line,
                           outing_stat_line=outing_stat_line)

# ***************-PITCHER ADVANCED STATS-*************** #
@pitcher.route('/pitcher/<id>/stats/advanced', methods=['GET', 'POST'])
@login_required
def pitcher_stats_advanced(id):
    '''
    PITCHER ADVANCED STATS:
    Displays advanced game/outing statistics

    PARAM:
        -id: the id (primary key) of the pitcher that wants
            to be viewed

    RETURN:
        -pitcher_stats_advanced.html which holds a table holding
            basic statistics
    '''

    # get the user object associated with the username in the url
    pitcher = Pitcher.query.filter_by(id=id).first()

    # either bug or user trying to access pitcher page that DNE
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    # get the outings associated with that player
    outings = pitcher.outings

    # get seasons associated with player
    seasons = []
    for outing in outings:
        if outing.season not in seasons:
            seasons.append(outing.season)

    # gets stats associated with pitcher
    avg_pitch_velo_career, avg_pitch_velo_outing, avg_pitch_velo_season = avgPitchVeloPitcher(pitcher)
    strike_percentage_career, strike_percentage_outing, strike_percentage_season = pitchStrikePercentageSeason(pitcher)
    pitch_usage_career, pitch_usage_outing, pitch_usage_season = pitchUsageSeason(pitcher)

    return render_template('pitcher/pitcher_stats_advanced.html',
                           title=pitcher,
                           pitcher=pitcher,
                           seasons=seasons,
                           avg_pitch_velo_career=avg_pitch_velo_career,
                           avg_pitch_velo_season=avg_pitch_velo_season,
                           avg_pitch_velo_outing=avg_pitch_velo_outing,
                           strike_percentage_career=strike_percentage_career,
                           strike_percentage_season=strike_percentage_season,
                           strike_percentage_outing=strike_percentage_outing,
                           pitch_usage_career=pitch_usage_career,
                           pitch_usage_outing=pitch_usage_outing,
                           pitch_usage_season=pitch_usage_season)


@pitcher.route('/pitcher/<id>/videos', methods=["GET", "POST"])
@login_required
def pitcher_videos(id):

    pitcher = Pitcher.query.filter_by(id=id).first()

    return render_template(
        '/pitcher/pitcher_videos.html',
        title=pitcher,
        pitcher=pitcher)
