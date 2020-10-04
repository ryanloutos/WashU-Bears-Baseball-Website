from app import db

from flask import flash
from flask import url_for
from flask import redirect
from flask import Blueprint
from flask import render_template

from app.forms import NewPitcherForm
from app.forms import EditPitcherForm

from app.models import User
from app.models import Pitch
from app.models import Video
from app.models import Outing
from app.models import Season
from app.models import Pitcher
from app.models import Opponent

from flask_login import current_user
from flask_login import login_required

from app.stats.pitching_stats import veloOverCareer
from app.stats.pitching_stats import seasonStatLine
from app.stats.pitching_stats import pitchUsageSeason
from app.stats.pitching_stats import avgPitchVeloPitcher
from app.stats.pitching_stats import pitchStrikePercentageSeason

from app.stats.scouting_stats import whiff_coords_by_pitch_pitcher
from app.stats.scouting_stats import pitcher_dynamic_zone_scouting

import os

pitcher = Blueprint("pitcher", __name__)


# ***************-PITCHER HOMEPAGE-*************** # DONE
@pitcher.route('/pitcher/<id>', methods=['GET', 'POST'])
@login_required
def pitcher_home(id):
    pitcher = Pitcher.query.filter_by(id=id).first()
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    outings = Outing.query.filter(
        Outing.pitcher_id == pitcher.id).order_by(Outing.date)

    # get the number of outings they have thrown
    num_outings = 0
    for o in outings:
        num_outings += 1

    velo_over_career = veloOverCareer(outings)

    file_loc = os.path.join(
        "images",
        "pitcher_photos",
        f"{pitcher.id}.png"
    )

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

    return render_template(
        'pitcher/pitcher_home.html',
        title=pitcher,
        pitcher=pitcher,
        outings=outings,
        file_loc=file_loc,
        velo_over_career=velo_over_career,
        recent_outings=recent_outings
    )


# ***************-NEW PITCHER-*************** #
@pitcher.route('/new_pitcher', methods=['GET', 'POST'])
@login_required
def new_pitcher():
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('main.index'))

    form = NewPitcherForm()
    if form.validate_on_submit():
        pitcher = Pitcher(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            number=form.number.data,
            throws=form.throws.data,
            grad_year=form.grad_year.data,
            opponent_id=form.opponent.data.id,
            notes=form.notes.data,
            retired=form.retired.data
        )

        db.session.add(pitcher)
        db.session.commit()

        flash("New Pitcher Created!")
        return redirect(url_for('pitcher.pitcher_home', id=pitcher.id))

    return render_template(
        'pitcher/new_pitcher.html',
        title="New Pitcher",
        form=form
    )

# ***************-EDIT PITCHER-*************** #
@pitcher.route('/edit_pitcher/<id>', methods=['GET', 'POST'])
@login_required
def edit_pitcher(id):
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('main.index'))

    pitcher = Pitcher.query.filter_by(id=id).first()
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    form = EditPitcherForm()
    if form.validate_on_submit():
        if form.photo.data:
            file_name = pitcher.id
            file_loc = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "static",
                "images",
                "pitcher_photos",
                f"{file_name}.png"
            )

            form.photo.data.save(file_loc)

        pitcher.firstname = form.firstname.data
        pitcher.lastname = form.lastname.data
        pitcher.throws = form.throws.data
        pitcher.grad_year = form.grad_year.data
        pitcher.opponent_id = form.opponent.data.id
        pitcher.number = form.number.data
        pitcher.retired = form.retired.data
        pitcher.notes = form.notes.data

        db.session.commit()

        flash("Changes made!")
        return redirect(url_for('pitcher.pitcher_home', id=id))

    opponents = Opponent.query.order_by(Opponent.name).all()
    return render_template(
        'pitcher/edit_pitcher.html',
        title="Edit Pitcher",
        pitcher=pitcher,
        opponents=opponents,
        form=form
    )

# ***************-DELETE PITCHER-*************** #
@pitcher.route('/delete_pitcher/<id>', methods=['GET', 'POST'])
@login_required
def delete_pitcher(id):
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('main.index'))

    pitcher = Pitcher.query.filter_by(id=id).first()
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    outings = Outing.query.filter_by(pitcher_id=id).all()
    if len(outings) > 0:
        flash("""You can't delete this pitcher because they
                have outings associated with them """)
        return redirect(url_for('pitcher.pitcher_home', id=id))

    videos = Video.query.filter_by(pitcher_id=id).all()
    if len(videos) > 0:
        flash("""You can't delete this pitcher because they 
            have videos associated with them """)
        return redirect(url_for('pitcher.pitcher_home', id=id))

    db.session.delete(pitcher)
    db.session.commit()
    flash("Pitcher has been deleted!")
    return redirect(url_for('main.index'))


# ***************-PITCHER OUTINGS-*************** #
@pitcher.route('/pitcher/<id>/outings', methods=['GET', 'POST'])
@login_required
def pitcher_outings(id):
    pitcher = Pitcher.query.filter_by(id=id).first()
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    outings = pitcher.outings
    seasons = []
    for outing in outings:
        if outing.season not in seasons:
            seasons.append(outing.season)

    return render_template(
        'pitcher/pitcher_outings.html',
        title=pitcher,
        pitcher=pitcher,
        seasons=seasons
    )


# ***************-PITCHER BASIC STATS-*************** #
@pitcher.route('/pitcher/<id>/stats/basic', methods=['GET', 'POST'])
@login_required
def pitcher_stats_basic(id):
    pitcher = Pitcher.query.filter_by(id=id).first()
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    outings = pitcher.outings
    seasons = []
    for outing in outings:
        if outing.season not in seasons:
            seasons.append(outing.season)

    season_stat_line, outing_stat_line = seasonStatLine(pitcher)

    return render_template(
        'pitcher/pitcher_stats_basic.html',
        title=pitcher,
        pitcher=pitcher,
        seasons=seasons,
        season_stat_line=season_stat_line,
        outing_stat_line=outing_stat_line
    )


# ***************-PITCHER ADVANCED STATS-*************** #
@pitcher.route('/pitcher/<id>/stats/advanced', methods=['GET', 'POST'])
@login_required
def pitcher_stats_advanced(id):
    pitcher = Pitcher.query.filter_by(id=id).first()
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    outings = pitcher.outings
    seasons = []
    for outing in outings:
        if outing.season not in seasons:
            seasons.append(outing.season)

    # gets stats associated with pitcher
    avg_pitch_velo_career, avg_pitch_velo_outing, avg_pitch_velo_season = avgPitchVeloPitcher(
        pitcher)
    strike_percentage_career, strike_percentage_outing, strike_percentage_season = pitchStrikePercentageSeason(
        pitcher)
    pitch_usage_career, pitch_usage_outing, pitch_usage_season = pitchUsageSeason(
        pitcher)

    return render_template(
        'pitcher/pitcher_stats_advanced.html',
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
        pitch_usage_season=pitch_usage_season
    )


# ***************-PITCHER VIDEOS-*************** #
@pitcher.route('/pitcher/<id>/videos', methods=["GET", "POST"])
@login_required
def pitcher_videos(id):
    pitcher = Pitcher.query.filter_by(id=id).first()
    videos = Video.query.filter_by(pitcher_id=id).all()
    seasons = []
    for v in videos:
        if v.season not in seasons:
            seasons.append(v.season)

    return render_template(
        '/pitcher/pitcher_videos.html',
        title=pitcher,
        pitcher=pitcher,
        seasons=seasons
    )

# ***************-PITCHER SCOUTING-*************** #
@pitcher.route("/pitcher/<id>/scouting")
@login_required
def pitcher_scouting(id):
    pitcher = Pitcher.query.filter_by(id=id).first()
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    dynamic_data = pitcher_dynamic_zone_scouting(pitcher)

    return render_template(
        '/pitcher/pitcher_scouting.html',
        title=pitcher,
        pitcher=pitcher,
        dynamic_data=dynamic_data
    )

# ***************-PITCHER TESTING-*************** #
@pitcher.route('/pitcher/<pitcher_id>/testing')
@login_required
def pitcher_testing(pitcher_id):
    pitcher = Pitcher.query.filter_by(id=pitcher_id).first()
    if not pitcher:
        flash('URL does not exist')
        return redirect(url_for('main.index'))

    data = whiff_coords_by_pitch_pitcher(pitcher)
    data2 = pitcher_dynamic_zone_scouting(pitcher)

    return render_template(
        "/pitcher/pitcher_testing.html",
        pitcher=pitcher,
        data=data,
        data2=data2
    )
