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
from app.stats import staffPitchStrikePercentage
from app.stats import outingPitchStatistics, outingTimeToPlate, veloOverTime
from app.stats import stats_opponent_scouting_stats, stats_opponent_batters_stat_lines
from app.stats import calcPitchPercentages, pitchUsageByCount, calcAverageVelo
from app.stats import calcPitchStrikePercentage, calcPitchWhiffRate
from app.stats import createPitchPercentagePieChart, velocityOverTimeLineChart
from app.stats import pitchStrikePercentageBarChart, avgPitchVeloPitcher
from app.stats import pitchUsageByCountLineCharts, pitchStrikePercentageSeason
from app.stats import pitchUsageSeason, seasonStatLine, staffBasicStats
from app.stats import staffPitchStrikePercentage
from app.stats import outingPitchStatistics, outingTimeToPlate, veloOverTime
from app.stats import batterSwingWhiffRatebyPitchbyCount, batter_summary_game_stats
from app.stats import batterSwingWhiffRatebyPitchbyCount2, batter_ball_in_play_stats


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

    batters_stat_line, batters_hard_hit, pitch_usage_count, swing_whiff_rate = stats_opponent_batters_stat_lines(opponent)

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
        title=hitter.name,
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
