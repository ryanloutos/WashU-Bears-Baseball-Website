from app import db

from flask import flash
from flask import url_for
from flask import redirect
from flask import Blueprint
from flask import render_template

from app.forms import NewOpponentForm
from app.forms import EditOpponentForm

from app.models import Game
from app.models import Pitcher
from app.models import User
from app.models import AtBat
from app.models import Pitch
from app.models import Batter
from app.models import Outing
from app.models import Season
from app.models import Opponent

from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

from werkzeug.urls import url_parse

from app.stats.hitting_stats import stats_opponent_batters_stat_lines

import os
import re

opponent = Blueprint("opponent", __name__)


# ***************-NEW OPPONENT-*************** #
@opponent.route("/new_opponent", methods=["GET", "POST"])
@login_required
def new_opponent():
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for("main.index"))

    form = NewOpponentForm()
    if form.validate_on_submit():

        opponent = Opponent(name=form.name.data)

        db.session.add(opponent)
        db.session.commit()

        file_name = opponent.id
        file_loc = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "static",
            "images",
            "team_logos",
            f"{file_name}.png"
        )
        form.logo.data.save(file_loc)

        for subform in form.batters:
            if (subform.firstname.data not in ["", None] and
                subform.lastname.data not in ["", None] and
                    subform.number.data not in ["", None]):

                initials = getInitialsFromNames(
                    subform.firstname.data, subform.lastname.data)

                batter = Batter(
                    opponent_id=opponent.id,
                    firstname=subform.firstname.data,
                    lastname=subform.lastname.data,
                    number=subform.number.data,
                    initials=initials,
                    bats=subform.bats.data,
                    grad_year=subform.grad_year.data,
                    notes=subform.notes.data,
                    retired=subform.retired.data
                )

                db.session.add(batter)

        for subform in form.pitchers:
            if (subform.firstname.data not in ["", None] and
                subform.lastname.data not in ["", None] and
                    subform.number.data not in ["", None]):

                pitcher = Pitcher(
                    opponent_id=opponent.id,
                    firstname=subform.firstname.data,
                    lastname=subform.lastname.data,
                    number=subform.number.data,
                    throws=subform.throws.data,
                    grad_year=subform.grad_year.data,
                    notes=subform.notes.data,
                    retired=subform.retired.data
                )
                db.session.add(pitcher)

        db.session.commit()

        flash("Congratulations, you just made a new opponent!")
        return redirect(url_for("opponent.opponent_home", id=opponent.id))

    return render_template(
        "opponent/new_opponent.html",
        title="New Opponent",
        form=form
    )

# ***************-EDIT OPPONENT-*************** #
@opponent.route("/edit_opponent/<id>", methods=["GET", "POST"])
@login_required
def edit_opponent(id):
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for("main.index"))

    opponent = Opponent.query.filter_by(id=id).first()
    if not opponent:
        flash("URL does not exist")
        return redirect(url_for("main.index"))

    form = EditOpponentForm()
    if form.validate_on_submit():
        if form.logo.data is not None:
            file_name = opponent.id
            file_loc = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "static",
                "images",
                "team_logos",
                f"{file_name}.png"
            )
            form.logo.data.save(file_loc)

        opponent.name = form.name.data
        db.session.commit()

        flash("Changes made!")
        return redirect(url_for("opponent.opponent_home", id=opponent.id))

    return render_template(
        "opponent/edit_opponent.html",
        title="Edit Opponent",
        opponent=opponent,
        form=form
    )

# ***************-DELETE OPPONENT-*************** #
@opponent.route("/delete_opponent/<id>", methods=["GET", "POST"])
@login_required
def delete_opponent(id):
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for("main.index"))

    opponent = Opponent.query.filter_by(id=id).first()
    if not opponent:
        flash("URL does not exist")
        return redirect(url_for("main.index"))

    pitchers = Pitcher.query.filter_by(opponent_id=id).all()
    if len(pitchers) > 0:
        flash("Can't delete opponent because there are pitchers on the team")
        return redirect(url_for('opponent.opponent_home', id=id))

    batters = Batter.query.filter_by(opponent_id=id).all()
    if len(batters) > 0:
        flash("Can't delete opponent because there are batters on the team")
        return redirect(url_for('opponent.opponent_home', id=id))

    games = Game.query.filter_by(opponent_id=id).all()
    if len(games) > 0:
        flash("Can't delete opponent because there are games associated with the team")
        return redirect(url_for('opponent.opponent_home', id=id))

    db.session.delete(opponent)
    db.session.commit()

    # delete the team logo
    file_loc = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..",
        "static",
        "images",
        "team_logos",
        f"{id}.png"
    )
    os.remove(file_loc)

    flash('Deleted opponent!')
    return redirect(url_for('main.index'))


# ***************-OPPONENT HOMEPAGE-*************** #
@opponent.route('/opponent/<id>', methods=['GET', 'POST'])
@login_required
def opponent_home(id):
    opponent = Opponent.query.filter_by(id=id).first()
    if not opponent:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    pitchers = Pitcher.query.filter_by(
        opponent_id=id).filter_by(retired=0).all()
    batters = Batter.query.filter_by(opponent_id=id).filter_by(retired=0).all()

    return render_template(
        'opponent/opponent_home.html',
        title=opponent,
        opponent=opponent,
        pitchers=pitchers,
        batters=batters
    )

# ***************-GAME RESULTS-*************** #
@opponent.route("/opponent/<id>/GamesResults", methods=["GET", "POST"])
@login_required
def opponent_games_results(id):
    opponent = Opponent.query.filter_by(id=id).first()
    if not opponent:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    seasons = []
    for game in opponent.games:
        season = game.get_season()
        if season not in seasons:
            seasons.append(season)

    return render_template(
        '/opponent/opponent_GamesResults.html',
        title=opponent,
        opponent=opponent,
        seasons=seasons
    )

# ***************-SCOUTING STATS-*************** #
@opponent.route("/opponent/<opponent_id>/ScoutingStats", methods=["GET", "POST"])
@login_required
def opponent_scouting_stats(opponent_id):
    opponent = Opponent.query.filter_by(id=opponent_id).first()
    if not opponent:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    batters_stat_line, batters_hard_hit = stats_opponent_batters_stat_lines(
        opponent)

    return render_template(
        '/opponent/opponent_ScoutingStats.html',
        title=opponent,
        opponent=opponent,
        batters_stat_line=batters_stat_line,
        batters_hard_hit=batters_hard_hit
    )


# ***************-ALL OPPONENTS-*************** #
@opponent.route('/all_opponents', methods=['GET', 'POST'])
@login_required
def all_opponents():
    opponents = Opponent.query.order_by(Opponent.name).all()
    if not opponents:
        flash("URL does not exist")
        return redurect(url_for('main.index'))

    return render_template(
        'opponent/all_opponents.html',
        title="All Opponents",
        opponents=opponents
    )

# ***************-OPPONENT ROSTER-*************** #
@opponent.route('/opponent/<id>/roster', methods=['GET', 'POST'])
@login_required
def opponent_roster(id):
    opponent = Opponent.query.filter_by(id=id).first()
    if not opponent:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        'opponent/opponent_roster.html',
        title=opponent,
        opponent=opponent
    )

# ***************-OPPONENT INACTIVE ROSTER-*************** #
@opponent.route("/opponent/<id>/inactive_roster")
@login_required
def opponent_inactive_hitters(id):
    opponent = Opponent.query.filter_by(id=id).first()
    if not opponent:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    return render_template(
        "opponent/opponent_inactive_roster.html",
        opponent=opponent
    )

# ***************-HELPFUL FUNCTIONS-*************** #


def getInitialsFromNames(firstname, lastname):
    first_initial = re.findall("^\w", firstname)
    last_initial = re.findall("^\w", lastname)
    return f"{first_initial[0]}{last_initial[0]}"
