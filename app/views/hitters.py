from flask import flash
from flask import url_for
from flask import request
from flask import redirect
from flask import Blueprint
from flask import render_template

from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

from werkzeug.urls import url_parse

from app import db

from app.forms import BatterForm
from app.forms import EditBatterForm
from app.forms import EditOpponentForm

from app.models import User
from app.models import Game
from app.models import AtBat
from app.models import Pitch
from app.models import Video
from app.models import Outing
from app.models import Season
from app.models import Batter
from app.models import Opponent

from app.stats.util import zero_division_handler

from app.stats.hitting_stats import batter_summary_game_stats
from app.stats.hitting_stats import batter_ball_in_play_stats
from app.stats.hitting_stats import stats_opponent_batters_stat_lines
from app.stats.hitting_stats import batterSwingWhiffRatebyPitchbyCount

from app.stats.scouting_stats import zone_division_stats_batter
from app.stats.scouting_stats import batter_dynamic_zone_scouting

import re

hitters = Blueprint("hitters", __name__)
hitter = Blueprint("hitter", __name__)

# *************************************TEAM BASED WASHU HITTERS PAGES ***************************************
@hitters.route('/hitters/home', methods=['GET', 'POST'])
@login_required
def hitters_home():
    '''
    HITTERS HOMEPAGE:

    RETURN:
        -opponent.html which displays the homepage/info page
            for that opponent
    '''
    # get the Opponent object assicated with the id
    opponent = Opponent.query.filter_by(id=1).first()

    # bug or user trying to view opponent that DNE
    if not opponent:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template('hitters/hitters_home.html',
                           title=opponent,
                           opponent=opponent)


@hitters.route("/hitters/games", methods=["GET", "POST"])
@login_required
def hitters_games():
    '''This is a depreciated route. It is not included in the nav, 
    and has no real value in the site.'''

    opponent = Opponent.query.filter_by(id=1).first()
    if not opponent:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    seasons = []
    for game in opponent.games:
        season = game.get_season()
        if season not in seasons:
            seasons.append(season)

    return render_template(
        '/hitters/hitters_games.html',
        title=opponent,
        opponent=opponent,
        seasons=seasons
    )


@hitters.route("/hitters/stats", methods=["GET", "POST"])
@login_required
def hitters_stats():

    opponent = Opponent.query.filter_by(id=1).first()
    if not opponent:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    batters_stat_line, batters_hard_hit, pitch_usage_count, swing_whiff_rate = stats_opponent_batters_stat_lines(
        opponent)

    return render_template(
        '/hitters/hitters_stats.html',
        title=opponent,
        opponent=opponent,
        pitch_usage_count=pitch_usage_count,
        swing_whiff_rate=swing_whiff_rate,
        batters_stat_line=batters_stat_line,
        batters_hard_hit=batters_hard_hit
    )


@hitters.route("/hitters/inactive_roster")
@login_required
def hitters_inactive_roster():
    '''Loads the inactive roster of WashU hitters. Ex players and such'''
    # get opponent object
    opponent = Opponent.query.filter_by(id=1).first()

    # either bug or admin trying to edit opponent that doesn't exist
    if not opponent:
        flash('URL does not exist')
        return redirect(url_for('main.index'))    # get opponent object

    return render_template(
        "hitters/hitters_inactive_roster.html",
        opponent=opponent
    )


@hitters.route('/hitters/edit', methods=['GET', 'POST'])
@login_required
def hitters_edit():
    '''This is a depreciated route. It should not ever be used. If washU
    is to be edited, it needs to be as an opponent.'''
    # if user is not an admin, they can't create a new opponent
    if not current_user.admin:
        flash('You are not an admin and cannot edit an opponent')
        return redirect(url_for('main.index'))

    # get opponent object
    opponent = Opponent.query.filter_by(id=1).first()

    # either bug or admin trying to edit opponent that doesn't exist
    if not opponent:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    # once 'create opponent' button is pressed
    form = EditOpponentForm()
    if form.validate_on_submit():

        file_name = opponent.id
        file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                "..",
                                "static",
                                "images",
                                "team_logos",
                                f"{file_name}.png")

        form.file.data.save(file_loc)

        # get the updated Opponent name and commit to database
        opponent.name = form.name.data
        db.session.commit()

        # redirect back to opponent page
        flash('Congratulations, you just edited Hitters!')
        return redirect(url_for('hitters.hitters_home'))

    return render_template('hitters/hitters_edit.html',
                           title='Edit Hitters',
                           opponent=opponent,
                           form=form)


# *************************************PLAYER BASED WASHU HITTERS PAGES **************************************

@hitter.route("/hitter/<id>/home")
@login_required
def hitter_home(id):

    # get the Batter object associated with the id passed in
    hitter = Batter.query.filter_by(id=id).first()

    # either bug or user trying to view a batter that DNE
    if not hitter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    games = hitter.get_games()

    game_stats = []
    for game in games:

        if game is not None and game.get_season().current_season:
            at_bats, pitches_seen = batter_summary_game_stats(game, hitter)
            game_stats.append({
                "game": game,
                "stats": {
                    "ab": at_bats,
                    "pitches": pitches_seen
                }
            })

    return render_template(
        'hitters/hitter/hitter.html',
        title=hitter,
        batter=hitter,
        game_stats=game_stats)


@hitter.route("/hitter/<batter_id>/game/<game_id>")
@login_required
def hitter_game_view(batter_id, game_id):

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
        "hitters/hitter/hitter_game_view.html",
        batter=batter,
        game=game,
        game_at_bats=game_at_bats,
        pitches=pitches,
        hits=hits
    )


@hitter.route("/hitter/<batter_id>/at_bats", methods=['GET', 'POST'])
@login_required
def hitter_at_bats(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()

    # either bug or user trying to view a batter that DNE
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        '/hitters/hitter/hitter_at_bats.html',
        batter=batter
    )


@hitter.route("/hitter/<batter_id>/at_bat/<ab_num>", methods=['GET', 'POST'])
@login_required
def hitter_at_bat(batter_id, ab_num):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    at_bat = AtBat.query.filter_by(id=ab_num).first()
    if not at_bat:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    pitches = []
    ab_res = 0
    for p in at_bat.pitches:
        pitches.append({
            "pitch_num": p.pitch_num,
            "pitch_type": p.pitch_type,
            "x": p.loc_x,
            "y": p.loc_y
        })
        if p.pitch_result in ["IP"]:
            ab_res = {
                "x": p.spray_x,
                "y": p.spray_y,
                "traj": p.traj,
                "hard_hit": p.hit_hard,
            }

    pitcher = at_bat.get_pitcher()

    return render_template(
        '/hitters/hitter/hitter_at_bat.html',
        at_bat=at_bat,
        pitcher=pitcher,
        batter=batter,
        title=batter,
        pitches=pitches,
        ab_res=ab_res
    )


@hitter.route("/hitter/<batter_id>/games", methods=["GET", "POST"])
@login_required
def hitter_games(batter_id):

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
        "hitters/hitter/hitter_games.html",
        batter=batter,
        games=games,
        game_stats=game_stats,
        seasons=seasons
    )


@hitter.route('/hitter/<id>/videos', methods=["GET", "POST"])
@login_required
def hitter_videos(id):

    batter = Batter.query.filter_by(id=id).first()
    videos = Video.query.filter_by(batter_id=id).all()
    video_ids = []
    seasons = []
    for v in videos:

        if v.season not in seasons:
            seasons.append(v.season)

        # https://gist.github.com/silentsokolov/f5981f314bc006c82a41
        # gets the id from a youtube linke
        regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
        match = regex.match(v.link)
        if not match:
            video_ids.append("")
        else:
            video_ids.append(match.group("id"))

    return render_template(
        'hitters/hitter/hitter_videos.html',
        title=batter,
        batter=batter,
        seasons=seasons,
        video_objects=videos,
        videos=video_ids
    )


@hitter.route("/hitter/<batter_id>/spray_chart", methods=['GET', 'POST'])
@login_required
def hitter_spray_chart(batter_id):

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
                locs.append(
                    {"x_loc": p.loc_x, "y_loc": p.loc_y, "type": p.pitch_type})

    # Change density vals to percentages
    for i in range(len(density_vals)):
        density_vals[i] = zero_division_handler(density_vals[i], d_total)

    return render_template(
        'hitters/hitter/hitter_spray_chart.html',
        title=batter,
        batter=batter,
        sprays=sprays,
        d_vals=density_vals,
        outcomes=outcomes,
        locs=locs
    )


@hitter.route("/hitter/<batter_id>/stats")
@login_required
def hitter_stats(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))
    seasons = batter.get_seasons()

    # Batter stat calculations

    pitch_usage_count, swing_whiff_rate = batterSwingWhiffRatebyPitchbyCount(batter)

    ball_in_play, hard_hit = batter_ball_in_play_stats(batter)

    return render_template(
        "hitters/hitter/hitter_stats.html",
        pitch_usage_count=pitch_usage_count,
        swing_whiff_rate=swing_whiff_rate,
        ball_in_play=ball_in_play,
        hard_hit=hard_hit,
        title=batter,
        batter=batter,
        seasons=seasons
    )


@hitter.route('/hitter/<id>/edit', methods=['GET', 'POST'])
@login_required
def hitter_edit(id):

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
        return redirect(url_for('hitters.hitters_home', id=batter.opponent_id))

    return render_template(
        'hitters/hitter/hitter_edit.html',
        title='Edit Hitter',
        batter=batter,
        form=form)


@hitter.route('/hitter/<id>/scouting')
@login_required
def hitter_scouting(id):
    batter = Batter.query.filter_by(id=id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    zone_division_stats = zone_division_stats_batter(batter)
    dynamic_data = batter_dynamic_zone_scouting(batter)
    # whiff_coords_by_pitch = whiff_coords_by_pitch_batter(batter)

    return render_template(
        'hitters/hitter/hitter_scouting.html',
        batter=batter,
        title=batter,
        dynamic_data=dynamic_data,
        zone_division_stats=zone_division_stats
        # whiff_coords_by_pitch=whiff_coords_by_pitch
    )
