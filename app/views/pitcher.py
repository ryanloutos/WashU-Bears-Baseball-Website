from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db

from app.forms import PitcherForm, EditPitcherForm
from app.models import User, Outing, Pitch, Season, Pitcher, Opponent, Video
from app.stats import avgPitchVeloPitcher, veloOverCareer
from app.stats import pitchStrikePercentageSeason
from app.stats import pitchUsageSeason, seasonStatLine

# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random
import re

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
    outings = Outing.query.filter(Outing.pitcher_id == pitcher.id).order_by(Outing.date)

    # get the number of outings they have thrown
    num_outings = 0
    for o in outings:
        num_outings += 1

    velo_over_career = veloOverCareer(outings)

    file_loc = os.path.join("images",
                            "pitcher_photos",
                            f"{pitcher.id}.png")

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
                           outings=outings,
                           file_loc=file_loc,
                           velo_over_career=velo_over_career,
                           recent_outings=recent_outings)

# ***************-NEW PITCHER-*************** #
@pitcher.route('/new_pitcher', methods=['GET','POST'])
@login_required
def new_pitcher():

    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('index'))

    form = PitcherForm()

    # set the opponent choices for the form
    opponents = Opponent.query.all()
    opponent_choices = []
    for o in opponents:
        opponent_choices.append((str(o.id),o))
    form.opponent.choices = opponent_choices

    if form.validate_on_submit():

        pitcher = Pitcher(
            name=form.name.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            number=form.number.data,
            throws=form.throws.data,
            grad_year=form.grad_year.data,
            opponent_id=form.opponent.data,
            retired=form.retired.data
        )

        db.session.add(pitcher)
        db.session.commit()

        flash("New Pitcher Created!")
        return redirect(url_for('main.index'))

    return render_template(
        'pitcher/new_pitcher.html',
        form=form)

# ***************-EDIT PITCHER-*************** #
@pitcher.route('/edit_pitcher/<id>', methods=['GET','POST'])
@login_required
def edit_pitcher(id):

    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('index'))
    
    form = EditPitcherForm()

    pitcher = Pitcher.query.filter_by(id=id).first()

    # set the opponent choices for the form
    opponents = Opponent.query.all()
    opponent_choices = []
    for o in opponents:
        opponent_choices.append((str(o.id),o))
    form.opponent.choices = opponent_choices

    if form.validate_on_submit():

        file_name = pitcher.id
        file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                "..",
                                "static",
                                "images",
                                "pitcher_photos",
                                f"{file_name}.png")
        
        form.file.data.save(file_loc)

        pitcher.throws = form.throws.data
        pitcher.grad_year = form.grad_year.data
        pitcher.opponent_id = form.opponent.data
        pitcher.retired = form.retired.data

        db.session.commit()

        flash("Changes made!")
        return redirect(url_for('pitcher.pitcher_home', id=id))
    
    return render_template(
        'pitcher/edit_pitcher.html',
        pitcher = pitcher,
        opponents = opponents,
        form = form
    )


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
    videos = Video.query.filter_by(pitcher_id=id).all()
    video_ids = []
    seasons = []
    for v in videos:

        if v.season not in seasons:
            seasons.append(v.season)

        # https://gist.github.com/silentsokolov/f5981f314bc006c82a41
        # gets the id from a youtube linke
        regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
        match = regex.match(v.link)
        if not match:
            video_ids.append("")
        else:
            video_ids.append(match.group("id"))

    return render_template(
        '/pitcher/pitcher_videos.html',
        title=pitcher,
        pitcher=pitcher,
        seasons=seasons,
        video_objects=videos,
        videos=video_ids
    )



