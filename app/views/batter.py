from app import db

from flask import flash
from flask import url_for
from flask import request
from flask import redirect
from flask import Blueprint
from flask import render_template

from app.forms import NewBatterForm
from app.forms import EditBatterForm

from app.models import Game
from app.models import User
from app.models import AtBat
from app.models import Pitch
from app.models import Video
from app.models import Outing
from app.models import Season
from app.models import Batter
from app.models import Opponent

from flask_login import current_user
from flask_login import login_required

from app.stats.hitting_stats import batter_summary_game_stats
from app.stats.hitting_stats import batter_ball_in_play_stats
from app.stats.hitting_stats import batterSwingWhiffRatebyPitchbyCount
from app.stats.hitting_stats import batterSwingWhiffRatebyPitchbyCount2

from app.stats.scouting_stats import zone_division_stats_batter
from app.stats.scouting_stats import batter_dynamic_zone_scouting
from app.stats.scouting_stats import whiff_coords_by_pitch_batter


batter = Blueprint('batter', __name__)


# ***************-NEW BATTER-*************** #
@batter.route("/new_batter", methods=["GET", "POST"])
@login_required
def new_batter():
    if not current_user.admin:
        flash("You are not an admin and cannot create a season")
        return redirect(url_for("main.index"))

    form = NewBatterForm()
    if form.validate_on_submit():

        batter = Batter(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            initials=f"{form.firstname.data[0]}{form.lastname.data[0]}",
            number=form.number.data,
            bats=form.bats.data,
            grad_year=form.grad_year.data,
            notes=form.notes.data,
            opponent_id=form.opponent.data.id,
            retired=form.retired.data
        )

        db.session.add(batter)
        db.session.commit()

        flash("New batter created!")
        return redirect(url_for("opponent.opponent_home", id=batter.opponent_id))

    return render_template(
        "opponent/batter/new_batter.html",
        title="New Batter",
        form=form
    )

# ***************-EDIT BATTER-*************** #
@batter.route("/edit_batter/<id>", methods=["GET", "POST"])
@login_required
def edit_batter(id):
    if not current_user.admin:
        flash("You are not an admin")
        return redirect(url_for("main.index"))

    batter = Batter.query.filter_by(id=id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for("main.index"))

    form = EditBatterForm()
    if form.validate_on_submit():

        batter.firstname = form.firstname.data
        batter.lastname = form.lastname.data
        batter.opponent = form.opponent.data
        batter.initials = f"{form.firstname.data[0]}{form.lastname.data[0]}"
        batter.number = form.number.data
        batter.bats = form.bats.data
        batter.grad_year = form.grad_year.data
        batter.notes = form.notes.data
        batter.retired = form.retired.data

        db.session.commit()

        flash("Batter has been adjusted")
        return redirect(url_for("batter.batter_home", id=id))

    can_edit_opponent = True
    at_bats = AtBat.query.filter_by(batter_id=id).all()
    if len(at_bats) > 0:
        can_edit_opponent = False

    opponents = Opponent.query.order_by(Opponent.name).all()
    return render_template(
        "opponent/batter/edit_batter.html",
        title="Edit Batter",
        batter=batter,
        opponents=opponents,
        form=form,
        can_edit_opponent=can_edit_opponent
    )

# ***************-DELETE BATTER-*************** #
@batter.route("/delete_batter/<id>", methods=["GET", "POST"])
@login_required
def delete_batter(id):
    if not current_user.admin:
        flash("You are not an admin and cannot delete a batter")
        return redirect(url_for("main.index"))

    batter = Batter.query.filter_by(id=id).first()
    if not batter:
        flash("Can't delete a batter that doesn't exist")
        return redirect(url_for("main.index"))

    at_bats = AtBat.query.filter_by(batter_id=id).all()
    if len(at_bats) > 0:
        flash("Can't delete batter because they have at bats associated with them")
        return redirect(url_for('batter.batter_home', id=id))

    videos = Video.query.filter_by(batter_id=id).all()
    if len(videos) > 0:
        flash("Can't delete batter because they have videos associated with them")
        return redirect(url_for('batter.batter_home', id=id))

    pitches = Pitch.query.filter_by(batter_id=id).all()
    if len(pitches) > 0:
        flash("Can't delete batter because they have pitches associated with them")
        return redirect(url_for('batter.batter_home', id=id))

    db.session.delete(batter)
    db.session.commit()

    flash('Batter deleted!')
    return redirect(url_for("opponent.opponent_home", id=batter.opponent_id))


# ***************-BATTER HOMEPAGE-*************** #
@batter.route('/batter/<id>', methods=['GET', 'POST'])
@login_required
def batter_home(id):
    batter = Batter.query.filter_by(id=id).first()
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

    return render_template(
        'opponent/batter/batter.html',
        title=batter,
        batter=batter,
        game_stats=game_stats
    )

# ***************-BATTER AT BATS-*************** #
@batter.route("/batter/<batter_id>/at_bats", methods=['GET', 'POST'])
@login_required
def batter_at_bats(batter_id):
    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        '/opponent/batter/batter_at_bats.html',
        batter=batter
    )

# ***************-BATTER AT BAT-*************** #
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
        '/opponent/batter/batter_at_bat.html',
        at_bat=at_bat,
        pitcher=pitcher,
        batter=batter,
        title=f"{batter} vs {at_bat.get_pitcher()}",
        pitches=pitches,
        ab_res=ab_res
    )

# ***************-BATTER PITCHES AGAINST-*************** #
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

# ***************-BATTER SPRAY CHART-*************** #
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
                    "zone_x": p.loc_x,
                    "zone_y": p.loc_y,
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
                locs.append({
                    "x_loc": p.loc_x,
                    "y_loc": p.loc_y,
                    "type": p.pitch_type})

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

# ***************-BATTER SEQUENCING-*************** #
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


# ***************-BATTER STATS-*************** #
@batter.route("/batter/<batter_id>/stats")
@login_required
def batter_stats(batter_id):
    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    seasons = batter.get_seasons()

    # Batter stat calculations
    pitch_usage_count, swing_whiff_rate = batterSwingWhiffRatebyPitchbyCount2(
        batter)
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

# ***************-BATTER GAMES-*************** #
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

# ***************-BATTER GAME VIEW-*************** #
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

# ***************-BATTER VIDEOS-*************** #
@batter.route('/batter/<id>/videos', methods=["GET", "POST"])
@login_required
def batter_videos(id):
    batter = Batter.query.filter_by(id=id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    videos = Video.query.filter_by(batter_id=id).all()
    seasons = []
    for v in videos:
        if v.season not in seasons:
            seasons.append(v.season)

    return render_template(
        'opponent/batter/batter_videos.html',
        title=batter,
        batter=batter,
        seasons=seasons
    )

# ***************-BATTER SCOUTING-*************** #
@batter.route("/batter/<batter_id>/scouting")
@login_required
def batter_scouting(batter_id):
    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    zone_division_stats = zone_division_stats_batter(batter)
    dynamic_data = batter_dynamic_zone_scouting(batter)
    # whiff_coords_by_pitch = whiff_coords_by_pitch_batter(batter)

    return render_template(
        'opponent/batter/batter_scouting.html',
        batter=batter,
        dynamic_data=dynamic_data,
        zone_division_stats=zone_division_stats
        # whiff_coords_by_pitch=whiff_coords_by_pitch
    )

# ***************-BATTER TESTING-*************** #
@batter.route("/batter/<batter_id>/tester")
@login_required
def batter_testing(batter_id):

    batter = Batter.query.filter_by(id=batter_id).first()
    if not batter:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    # data = whiff_coords_by_pitch_batter(batter)
    data = batter_dynamic_zone_scouting(batter)
    return render_template(
        "opponent/batter/batter_test.html",
        batter=batter,
        data=data
    )
