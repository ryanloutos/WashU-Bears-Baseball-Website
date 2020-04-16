from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db

from app.forms import LoginForm
from app.forms import PitchForm
from app.forms import BatterForm
from app.forms import OutingForm
from app.forms import SeasonForm
from app.forms import EditUserForm
from app.forms import OpponentForm
from app.forms import NewBatterForm
from app.forms import EditBatterForm
from app.forms import OutingPitchForm
from app.forms import EditOpponentForm
from app.forms import NewOutingFromCSV
from app.forms import RegistrationForm
from app.forms import ChangePasswordForm
from app.forms import NewOutingFromCSVPitches

from app.models import Game
from app.models import User
from app.models import AtBat
from app.models import Pitch
from app.models import Video
from app.models import Outing
from app.models import Season
from app.models import Batter
from app.models import Opponent

from app.stats.stats import veloOverTime
from app.stats.stats import seasonStatLine
from app.stats.stats import calcAverageVelo
from app.stats.stats import staffBasicStats
from app.stats.stats import pitchUsageSeason
from app.stats.stats import outingTimeToPlate
from app.stats.stats import pitchUsageByCount
from app.stats.stats import calcPitchWhiffRate
from app.stats.stats import avgPitchVeloPitcher
from app.stats.stats import calcPitchPercentages
from app.stats.stats import outingPitchStatistics
from app.stats.stats import velocityOverTimeLineChart
from app.stats.stats import batter_summary_game_stats
from app.stats.stats import calcPitchStrikePercentage
from app.stats.stats import batter_ball_in_play_stats
from app.stats.stats import staffPitchStrikePercentage
from app.stats.stats import pitchUsageByCountLineCharts
from app.stats.stats import pitchStrikePercentageSeason
from app.stats.stats import createPitchPercentagePieChart
from app.stats.stats import pitchStrikePercentageBarChart
from app.stats.stats import batterSwingWhiffRatebyPitchbyCount
from app.stats.stats import batterSwingWhiffRatebyPitchbyCount2

from app.stats.scouting_stats import zone_division_stats_batter
from app.stats.scouting_stats import whiff_coords_by_pitch_batter

import re

batter = Blueprint('batter', __name__)

# ***************-BATTER HOMEPAGE-*************** #
@batter.route('/batter/<id>', methods=['GET', 'POST'])
@login_required
def batter_home(id):
    '''
    BATTER HOMEPAGE:

    PARAM:
        -id: The batter id (primary key) for the batter
            that the user is trying to view

    RETURN:
        -batter.html which displays the homepage/info page
            for that batter
    '''

    # get the Batter object associated with the id passed in
    batter = Batter.query.filter_by(id=id).first()

    # either bug or user trying to view a batter that DNE
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    games = batter.get_games()

    game_stats = []
    for game in games:

        if game is not None and game.get_season().current_season:
            at_bats, pitches_seen = batter_summary_game_stats(game, batter)
            game_stats.append({
                "game": game,
                "stats": {
                    "ab": at_bats,
                    "pitches": pitches_seen
                }
            })
    return render_template('opponent/batter/batter.html',
                           title=batter,
                           batter=batter,
                           game_stats=game_stats)


@batter.route("/batter/<batter_id>/at_bats", methods=['GET', 'POST'])
@login_required
def batter_at_bats(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()

    # either bug or user trying to view a batter that DNE
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        '/opponent/batter/batter_at_bats.html',
        batter=batter
    )


@batter.route("/batter/<batter_id>/at_bat/<ab_num>", methods=['GET', 'POST'])
@login_required
def batter_at_bat(batter_id, ab_num):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    at_bat = AtBat.query.filter_by(id=ab_num).first()
    if not at_bat:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    pitches = []
    for p in at_bat.pitches:
        pitches.append({
            "pitch_num": p.pitch_num,
            "pitch_type": p.pitch_type,
            "x": p.loc_x,
            "y": p.loc_y
        })

    pitcher = at_bat.get_pitcher()

    return render_template(
        '/opponent/batter/batter_at_bat.html',
        at_bat=at_bat,
        pitcher=pitcher,
        batter=batter,
        title=f"{batter} vs {at_bat.get_pitcher()}",
        pitches=pitches
    )


@batter.route("/batter/<batter_id>/pitches_against", methods=['GET', 'POST'])
@login_required
def batter_pitches_against(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        'opponent/batter/batter_pitches_against.html',
        title=batter,
        batter=batter
    )


@batter.route("/batter/<batter_id>/spray_chart", methods=['GET', 'POST'])
@login_required
def batter_spray_chart(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    # Var setup
    sprays = []  # setup for dots on spraychart
    density_vals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    d_total = 0
    outcomes = []
    locs = []
    for ab in batter.at_bats:
        for p in ab.pitches:
            # if there was an ab_outcome
            if p.ab_result in ["1B", "2B", "3B", "HR", "IP->Out", "Error", "FC"]:
                # for d3 field object dots
                sprays.append({
                    "x": p.spray_x,
                    "y": p.spray_y,
                    "traj": p.traj,
                    "hard_hit": p.hit_hard
                })

                # For density chart
                if p.fielder not in ["", None]:
                    density_vals[int(p.fielder)] += 1
                    d_total += 1

            # for table containing all the outcomes from spray chart
            if p.ab_result not in ["", None]:
                outcomes.append(p)

            # for pitch locations against
            if p.loc_x not in [None, ""] and p.loc_y not in [None, ""]:
                locs.append({"x_loc": p.loc_x, "y_loc": p.loc_y, "type": p.pitch_type})

    # Change density vals to percentages
    for i in range(len(density_vals)):
        if d_total != 0:
            density_vals[i] = density_vals[i] / d_total

    return render_template(
        'opponent/batter/batter_spray_chart.html',
        title=batter,
        batter=batter,
        sprays=sprays,
        d_vals=density_vals,
        outcomes=outcomes,
        locs=locs
    )


@batter.route("/batter/<batter_id>/sequencing", methods=['GET', 'POST'])
@login_required
def batter_sequencing(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        'opponent/batter/batter_sequencing.html',
        title=batter,
        batter=batter
    )

# ***************-DELETE BATTER-*************** #
@batter.route('/delete_batter/<id>', methods=['GET', 'POST'])
@login_required
def delete_batter(id):
    '''
    DELETE BATTER
    Can delete an existing batter through this function

    PARAM:
        -id: the batter id (primary key) in which the user
            wants to delete

    RETURN:
        -deletes the batter and redirects to opponent page which the outing
            was associated with
    '''
    # only admins can go back and edit outing data
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('main.index'))

    # get the batter object associated with the id
    batter = Batter.query.filter_by(id=id).first()

    # bug of trying to delete batter that doesn't exist
    if not batter:
        flash("Can't delete a batter that doesn't exist")
        return redirect(url_for('main.index'))

    # delete the batter from database
    db.session.delete(batter)
    db.session.commit()

    return redirect(url_for('opponent.opponent_home', id=batter.opponent_id))

# ***************-EDIT BATTER-*************** #
@batter.route('/edit_batter/<id>', methods=['GET', 'POST'])
@login_required
def edit_batter(id):
    '''
    EDIT BATTER:
    Can edit an already existing batter

    PARAM:
        -id: The batter id (primary key) that wants to be
            edited

    RETURN:
        -edit_batter.html and redirects to opponent page
            once an opponent was successfully edited
    '''
    # make sure user is admin
    if not current_user.admin:
        flash("You are not an admin")
        return redirect(url_for('main.index'))

    # get the correct form
    form = EditBatterForm()

    # get the batter object
    batter = Batter.query.filter_by(id=id).first()

    # bug or trying to edit batter that doesn't exist
    if not batter:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    # set the opponent choices correctly
    opponent_choices = []
    opponents = Opponent.query.all()
    for o in opponents:
        opponent_choices.append((str(o.id), o.name))
    form.opponent.choices = opponent_choices

    # submit is clicked
    if form.validate_on_submit():

        # update info with data from form
        batter.firstname = form.firstname.data
        batter.lastname = form.lastname.data
        batter.number = form.number.data
        batter.short_name = form.nickname.data
        batter.bats = form.bats.data
        batter.grad_year = form.grad_year.data
        batter.retired = form.retired.data

        # commit the changes
        db.session.commit()

        flash('Batter has been adjusted')
        return redirect(url_for('opponent.opponent_home', id=batter.opponent_id))

    return render_template('opponent/batter/edit_batter.html',
                           title='Edit Batter',
                           batter=batter,
                           form=form)

# ***************-NEW BATTER-*************** #
@batter.route('/new_batter', methods=['GET', 'POST'])
@login_required
def new_batter():
    '''
    NEW BATTER:
    Can create a new batter for a specific opponent

    PARAM:
        -None

    RETURN:
        -new_batter.html
    '''
    # if user is not an admin, they can't create a new season
    if not current_user.admin:
        flash('You are not an admin and cannot create a season')
        return redirect(url_for('main.index'))

    # get the correct form
    form = NewBatterForm()

    # set the opponent choices correctly
    opponent_choices = []
    opponents = Opponent.query.all()
    for o in opponents:
        opponent_choices.append((str(o.id), o.name))
    form.opponent.choices = opponent_choices

    # when the Create Season button is pressed...
    if form.validate_on_submit():

        # insert data from form into season table
        batter = Batter(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            initials=form.initials.data,
            short_name=form.shortname.data,
            number=form.number.data,
            bats=form.bats.data,
            grad_year=form.grad_year.data,
            opponent_id=form.opponent.data,
            retired=form.retired.data)

        # send Season object to data table
        db.session.add(batter)
        db.session.commit()

        # redirect back to login page
        flash('New batter created!')
        return redirect(url_for('opponent.opponent_home', id=batter.opponent_id))

    return render_template('opponent/batter/new_batter.html',
                           title='New Batter',
                           form=form)


# ***************-HELPFUL FUNCTIONS-*************** #
def getAvailablePitchers():
    '''
    Gets all of the string names you are allowed to create outings for

    PARAM:
        -None

    RETURN:
        - [array] -- [strings of pitchers names]
    '''

    # gets all the User objects that are players on the team
    pitchers_objects = Pitcher.query.all()

    # set the available choices that someone can create an outing for
    available_pitchers = []

    if current_user.admin:
        for p in pitchers_objects:
            available_pitchers.append((f"{p.id}", p))

    return available_pitchers


def getAvailableBatters(outing_id):
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first_or_404()

    batters_tuples = []
    for batter in opponent.batters:
        batters_tuples.append((batter.id, batter))

    return batters_tuples


def updateCount(balls, strikes, pitch_result, ab_result, season):
    if ab_result is not '':
        if (season.semester == 'Fall'):
            balls = 1
            strikes = 1
        else:
            balls = 0
            strikes = 0
    else:
        if pitch_result is 'B':
            balls += 1
        else:
            if strikes is not 2:
                strikes += 1
    count = f'{balls}-{strikes}'
    return (balls, strikes, count)


def getCurrentSeason():
    current_season = Season.query.filter_by(current_season=True).first()
    return current_season


def getOldSeasons():
    old_seasons = Season.query.filter_by(current_season=False).order_by(Season.year).all()
    return old_seasons


@batter.route("/batter/<batter_id>/stats")
@login_required
def batter_stats(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))
    seasons = batter.get_seasons()

    # Batter stat calculations
    pitch_usage_count, swing_whiff_rate = batterSwingWhiffRatebyPitchbyCount2(batter)
    ball_in_play, hard_hit = batter_ball_in_play_stats(batter)

    return render_template(
        "opponent/batter/batter_stats.html",
        pitch_usage_count=pitch_usage_count,
        swing_whiff_rate=swing_whiff_rate,
        ball_in_play=ball_in_play,
        hard_hit=hard_hit,
        title=batter,
        batter=batter,
        seasons=seasons
        )


@batter.route("/batter/<batter_id>/games", methods=["GET", "POST"])
@login_required
def batter_games(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    games = batter.get_games()

    game_stats = []
    seasons = []
    for game in games:
        # line here for some weird error with appending games ending in None
        if game is not None:
            at_bats, pitches_seen = batter_summary_game_stats(game, batter)
            game_stats.append({
                "game": game,
                "stats": {
                    "ab": at_bats,
                    "pitches": pitches_seen
                }
            })
            if game.get_season() not in seasons:
                seasons.append(game.get_season())

    return render_template(
        "opponent/batter/batter_games.html",
        batter=batter,
        games=games,
        game_stats=game_stats,
        seasons=seasons
    )


@batter.route("/batter/<batter_id>/game/<game_id>")
@login_required
def batter_game_view(batter_id, game_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    game = Game.query.filter_by(id=game_id).first()
    if not game:
        flash("URL does not exist")
        return redirect(url_for("main.index"))

    game_at_bats = []
    pitches = []
    hits = []
    pitch_index = 1
    for at_bat in batter.at_bats:
        # if the game the at_bat is in is the same as the current game
        if at_bat.get_game() == game:
            game_at_bats.append(at_bat)

            # for pitches for locations chart
            for p in at_bat.pitches:
                pitcher = p.get_pitcher()
                pitches.append({
                    "pitch_num": pitch_index,
                    "pitch_type": p.pitch_type,
                    "x": p.loc_x,
                    "y": p.loc_y,
                    "hard_hit": p.hit_hard,
                    "pitcher_hand": pitcher.throws
                })
                pitch_index += 1

                # if there was an ab_coutome
                if p.ab_result in ["1B", "2B", "3B", "HR", "IP->Out", "Error", "FC"]:
                    hits.append({
                        "x": p.spray_x,
                        "y": p.spray_y,
                        "traj": p.traj,
                        "hard_hit": p.hit_hard
                    })

    return render_template(
        "opponent/batter/batter_game_view.html",
        batter=batter,
        game=game,
        game_at_bats=game_at_bats,
        pitches=pitches,
        hits=hits
    )


@batter.route('/batter/<id>/videos', methods=["GET", "POST"])
@login_required
def batter_videos(id):

    batter = Batter.query.filter_by(id=id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))
    videos = Video.query.filter_by(batter_id=id).all()
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
        'opponent/batter/batter_videos.html',
        title=batter,
        batter=batter,
        seasons=seasons,
        video_objects=videos,
        videos=video_ids
    )


@batter.route("/batter/<batter_id>/scouting")
@login_required
def batter_scouting(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    zone_division_stats = zone_division_stats_batter(batter)
    whiff_coords_by_pitch = whiff_coords_by_pitch_batter(batter)

    return render_template(
        'opponent/batter/batter_scouting.html',
        batter=batter,
        zone_division_stats=zone_division_stats,
        whiff_coords_by_pitch=whiff_coords_by_pitch
    )


@batter.route("/batter/<batter_id>/tester")
@login_required
def batter_testing(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    data = whiff_coords_by_pitch_batter(batter)
    return render_template(
        "opponent/batter/batter_test.html",
        batter=batter,
        data=data
    )