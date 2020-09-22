from app import db

from flask import Blueprint
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from flask import jsonify

from flask_login import login_required
from flask_login import current_user

from flask_api import status

from app.forms import PitcherNewVideoForm
from app.forms import BatterNewVideoForm
from app.forms import PitcherEditVideoForm
from app.forms import BatterEditVideoForm

from app.models import Video
from app.models import Season
from app.models import Batter
from app.models import Pitcher
from app.models import Opponent

video = Blueprint("video", __name__)


# ***************-NEW VIDEO PITCHER-*************** #
@video.route("/new_video_pitcher", methods=["GET", "POST"])
@login_required
def new_video_pitcher():
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('main.index'))

    form = PitcherNewVideoForm()
    if form.validate_on_submit():

        # check to make sure an outing was selected (it is optional)
        if not form.outing.data:
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
        return redirect(url_for(
            "pitcher.pitcher_home",
            id=form.pitcher.data.id)
        )

    return render_template(
        "video/new_video_pitcher.html",
        title="New Video Pitcher",
        form=form
    )


# ***************-NEW VIDEO BATTER-*************** #
@video.route("/new_video_batter", methods=["GET", "POST"])
@login_required
def new_video_batter():
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('main.index'))

    form = BatterNewVideoForm()
    if form.validate_on_submit():

        video = Video(
            title=form.title.data,
            date=form.date.data,
            season_id=form.season.data.id,
            batter_id=form.batter.data.id,
            link=form.link.data
        )

        db.session.add(video)
        db.session.commit()

        flash("Video Posted!")
        return redirect(url_for(
            "hitter.hitter_home",
            id=form.batter.data.id)
        )

    return render_template(
        "video/new_video_batter.html",
        title="New Video Batter",
        form=form
    )

# ***************-EDIT VIDEO PITCHER-*************** #
@video.route("/edit_video_pitcher/<id>", methods=["GET", "POST"])
@login_required
def edit_video_pitcher(id):
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('main.index'))

    video = Video.query.filter_by(id=id).first()
    if not video:
        flash("Video doesn't exist")
        return redirect(url_for('main.index'))

    form = PitcherEditVideoForm()
    if form.validate_on_submit():

        # check to make sure an outing was selected (it is optional)
        if not form.outing.data:
            outing_id = ""
        else:
            outing_id = form.outing.data.id

        video.title = form.title.data
        video.date = form.date.data
        video.season_id = form.season.data.id
        video.outing_id = outing_id
        video.pitcher_id = form.pitcher.data.id
        video.link = form.link.data

        db.session.commit()

        flash("Video saved!")
        return redirect(url_for(
            "pitcher.pitcher_videos",
            id=form.pitcher.data.id)
        )

    # these are used to create the select inputs for the form with prev one already selected
    pitcher = Pitcher.query.filter_by(id=video.pitcher_id).first()
    seasons = Season.query.all()
    opponents = Opponent.query.order_by(Opponent.name).all()

    return render_template(
        "video/edit_video_pitcher.html",
        title="Edit Video Pitcher",
        form=form,
        video=video,
        pitcher=pitcher,
        opponents=opponents,
        seasons=seasons
    )

# ***************-EDIT VIDEO BATTER-*************** #
@video.route("/edit_video_batter/<id>", methods=["GET", "POST"])
@login_required
def edit_video_batter(id):
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('main.index'))

    video = Video.query.filter_by(id=id).first()
    if not video:
        flash("Video doesn't exist")
        return redirect(url_for('main.index'))

    form = BatterEditVideoForm()
    if form.validate_on_submit():
        video.title = form.title.data
        video.date = form.date.data
        video.season_id = form.season.data.id
        video.batter_id = form.batter.data.id
        video.link = form.link.data

        db.session.commit()

        flash("Video saved!")
        return redirect(url_for(
            "batter.batter_videos",
            id=form.batter.data.id)
        )

    # these are used to create the select inputs for the form with prev one already selected
    batter = Batter.query.filter_by(id=video.batter_id).first()
    seasons = Season.query.all()
    opponents = Opponent.query.order_by(Opponent.name).all()
    return render_template(
        "video/edit_video_batter.html",
        title="Edit Video Batter",
        form=form,
        video=video,
        opponents=opponents,
        seasons=seasons,
        batter=batter
    )

# ***************-DELETE VIDEO-*************** #
@video.route("/delete_video/<id>", methods=["GET", "POST"])
@login_required
def delete_video(id):
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('main.index'))

    video = Video.query.filter_by(id=id).first()
    if not video:
        flash("Video does not exist")
        return redirect(url_for('main.index'))

    db.session.delete(video)
    db.session.commit()

    flash("Video deleted!")
    return redirect(url_for('main.index'))


# ***************-API ENDPOINTS-*************** #

# Used to get all the videos for a pitcher for a specific season
@video.route("/videos/pitcher/<pitcher_id>/season/<season_id>", methods=['GET'])
@login_required
def videos_in_season_pitcher(season_id, pitcher_id):
    season = Season.query.filter_by(id=season_id).first()
    pitcher = Pitcher.query.filter_by(id=pitcher_id).first()
    if not season:
        return "season_id invalid", status.HTTP_400_BAD_REQUEST
    if not pitcher:
        return "pitcher_id invalid", status.HTTP_400_BAD_REQUEST

    videos = Video.query.filter_by(season_id=season.id).filter_by(
        pitcher_id=pitcher.id).order_by(Video.date).all()

    return_videos = []
    for video in videos:
        return_videos.append(video.to_dict())

    return jsonify(return_videos), status.HTTP_200_OK

# Used to retreive all videos for a batter for a specific season
@video.route("/videos/batter/<batter_id>/season/<season_id>")
@login_required
def videos_in_season_batter(batter_id, season_id):
    season = Season.query.filter_by(id=season_id).first()
    batter = Batter.query.filter_by(id=batter_id).first()
    if not season:
        return "season_id invalid", status.HTTP_400_BAD_REQUEST
    if not batter:
        return "batter_id invalid", status.HTTP_400_BAD_REQUEST

    videos = Video.query.filter_by(season_id=season.id).filter_by(
        batter_id=batter.id).order_by(Video.date).all()

    return_videos = []
    for video in videos:
        return_videos.append(video.to_dict())

    return jsonify(return_videos), status.HTTP_200_OK
