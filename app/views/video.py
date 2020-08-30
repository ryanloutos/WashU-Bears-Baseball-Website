from flask import Blueprint
from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.forms import PitcherNewVideoForm, BatterNewVideoForm
from app.models import Video, Season, Batter, Pitcher

video = Blueprint("video", __name__)


# ***************-NEW VIDEO PITCHER-*************** #
@video.route("/new_video_pitcher", methods=["GET", "POST"])
@login_required
def new_video_pitcher():
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


# API endpoint to retrieve all the video links for a pitcher in a season
@video.route("/videos/season/<season_id>/pitcher/<pitcher_id>")
@login_required
def videos_in_season_pitcher(season_id, pitcher_id):
    season = Season.query.filter_by(id=season_id).first()
    pitcher = Pitcher.query.filter_by(id=pitcher_id).first()
    if not season:
        return jsonify({
            "status": "failure",
            "error": "Season id provided is invalid"
        })
    if not pitcher:
        return jsonify({
            "status": "failure",
            "error": "Pitcher id provided is invalid"
        })

    videos = Video.query.filter_by(season_id=season.id).filter_by(
        pitcher_id=pitcher.id).order_by(Video.date).all()

    video_ids = []
    video_names = []

    for v in videos:
        regex = re.compile(
            r"""(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)
            /(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})""")
        match = regex.match(v.link)
        if not match:
            video_ids.append("")
        else:
            video_ids.append(match.group("id"))

        video_names.append(v.__repr__())

    return jsonify({
        "status": "success",
        "video_names": video_names,
        "video_ids": video_ids
    })


# API endpoint to retreive all videos for a batter for a season
@video.route("/videos/season/<season_id>/batter/<batter_id>")
@login_required
def videos_in_season_batter(season_id, batter_id):
    season = Season.query.filter_by(id=season_id).first()
    batter = Batter.query.filter_by(id=batter_id).first()
    if not season:
        return jsonify({
            "status": "failure",
            "error": "Season id provided is invalid"
        })
    if not batter:
        return jsonify({
            "status": "failure",
            "error": "Batter id provided is invalid"
        })

    videos = Video.query.filter_by(season_id=season.id).filter_by(
        batter_id=batter.id).order_by(Video.date).all()

    video_ids = []
    video_names = []

    for v in videos:
        regex = re.compile(
            r"""(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)
            /(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})""")
        match = regex.match(v.link)
        if not match:
            video_ids.append("")
        else:
            video_ids.append(match.group("id"))

        video_names.append(v.__repr__())

    return jsonify({
        "status": "success",
        "video_names": video_names,
        "video_ids": video_ids
    })
