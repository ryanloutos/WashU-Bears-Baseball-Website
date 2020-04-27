from flask import Blueprint, make_response
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.forms import LoginForm, RegistrationForm, OutingForm, PitchForm
from app.forms import NewOutingFromCSV
from app.forms import OutingPitchForm, NewOutingFromCSVPitches, EditUserForm
from app.forms import ChangePasswordForm, EditBatterForm, EditOpponentForm
from app.forms import NewBatterForm
from app.models import User, Outing, Pitch, Season, Opponent, Batter, AtBat, Pitcher, Game, Video
from app.stats import calcPitchPercentages, pitchUsageByCount, calcAverageVelo
from app.stats import calcPitchStrikePercentage, calcPitchWhiffRate
from app.stats import createPitchPercentagePieChart, velocityOverTimeLineChart
from app.stats import pitchStrikePercentageBarChart, avgPitchVeloPitcher
from app.stats import pitchUsageByCountLineCharts, pitchStrikePercentageSeason
from app.stats import pitchUsageSeason, seasonStatLine, staffBasicStats
from app.stats import staffPitchStrikePercentage
from app.stats import outingPitchStatistics, outingTimeToPlate, veloOverTime
from datetime import datetime
import json
# Handle CSV uploads
import csv
import os
# for file naming duplication problem
import random
import re
import os
import csv
import json
import math
import random

from app import db

from flask import flash
from flask import request
from flask import url_for
from flask import redirect
from flask import Blueprint
from flask import make_response
from flask import render_template

from datetime import datetime

from app.forms import PitchForm
from app.forms import OutingForm
from app.forms import OutingPitchForm
from app.forms import NewOutingFromCSV
from app.forms import NewOutingFromCSVPitches

from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

from werkzeug.urls import url_parse

from app.models import Game
from app.models import User
from app.models import AtBat
from app.models import Video
from app.models import Pitch
from app.models import Batter
from app.models import Outing
from app.models import Season
from app.models import Pitcher
from app.models import Opponent

from app.stats.stats import veloOverTime
from app.stats.stats import outingTimeToPlate
from app.stats.stats import outingPitchStatistics


outing = Blueprint("outing", __name__)

# ***************-OUTING HOMEPAGE-*************** #
@outing.route('/outing/<id>', methods=['GET', 'POST'])
@login_required
def outing_home(id):
    '''
    OUTING HOMEPAGE:

    PARAM:
        -outing_id: The outing id (primary key) of the outing
            that is requested to be displayed

    RETURN:
        -outing_home.html which displays the homepage for
            the outing
    '''
    # get the outing object associated by the id in the url
    outing = Outing.query.filter_by(id=id).first()

    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('main.index'))

    # get opponent associated with outing
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first()

    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('main.index'))
    
    # Get statistical data
    pitch_stats = outingPitchStatistics(outing)
    time_to_plate = outingTimeToPlate(outing)

    pitch_usage_pie_labels = []
    pitch_usage_pie_data = []
    strike_percentage_polar_labels = []
    strike_percentage_polar_data = []
    for p in pitch_stats:
        pitch_usage_pie_labels.append(p['pitch_type'])
        strike_percentage_polar_labels.append(p['pitch_type'])
        if p['num_thrown'] in [0, None, "", "X", "x"]:
            pitch_usage_pie_data.append(0)
            strike_percentage_polar_data.append(0)
        else:
            pitch_usage_pie_data.append(p['num_thrown'])
            strike_percentage_polar_data.append(p['strike_percentage'])

    # setting up horizontal axis for line chart
    horizontal_axis = []
    i = 1
    for ab in outing.at_bats:
        for p in ab.pitches:
            # line chart
            horizontal_axis.append(i)
            i += 1



    velos = veloOverTime(outing)

    # render template with all the statistical data calculated from the outing
    return render_template(
        'outing/outing_home.html',
        title=outing,
        outing=outing,
        opponent=opponent,
        pitch_stats=pitch_stats,
        time_to_plate=time_to_plate,
        velos=velos,
        labels=horizontal_axis,
        pitch_usage_pie_data=pitch_usage_pie_data,
        pitch_usage_pie_labels=pitch_usage_pie_labels,
        strike_percentage_polar_labels=strike_percentage_polar_labels,
        strike_percentage_polar_data=strike_percentage_polar_data
    )

# ***************-OUTING PBP-*************** #
@outing.route('/outing/<id>/pbp', methods=['GET', 'POST'])
@login_required
def outing_pbp(id):
    '''
    OUTING PITCH BY PITCH:

    PARAM:
        -outing_id: The outing id (primary key) of the outing
            that is requested to be displayed

    RETURN:
        -outing.html which displays all of the pitches and
            at bats from the outing
    '''
    # get the outing object associated by the id in the url
    outing = Outing.query.filter_by(id=id).first()
    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('main.index'))

    opponent = Opponent.query.filter_by(id=outing.opponent_id).first()

    # for pitch location graph
    pitches = []
    for ab in outing.at_bats:
        for p in ab.pitches:
            batter = Batter.query.filter_by(id=p.batter_id).first()
            pitches.append({
                "pitch_num": p.pitch_num,
                "pitch_type": p.pitch_type,
                "x": p.loc_x,
                "y": p.loc_y,
                "batter_hand": batter.bats
            })

    # render template with all the statistical data calculated from the outing
    return render_template(
        'outing/outing_pbp.html',
        title=outing,
        outing=outing,
        opponent=opponent,
        pitches=pitches
    )

# ***************-OUTING ADVANCED STATS-*************** #
@outing.route('/outing/<id>/stats/advanced', methods=['GET', 'POST'])
@login_required
def outing_stats_advanced(id):
    '''
    OUTING ADVANCED STATS:

    PARAM:
        -outing_id: The outing id (primary key) of the outing
            that is requested to be displayed

    RETURN:
        -outing.html which displays some advanced statistics
            for a specific outing
    '''
    # get the outing object associated by the id in the url
    outing = Outing.query.filter_by(id=id).first()
    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('main.index'))

    opponent = Opponent.query.filter_by(id=outing.opponent_id).first()

    # Get statistical data
    pitch_stats = outingPitchStatistics(outing)
    time_to_plate = outingTimeToPlate(outing)

    # setting up horizontal axis for line chart
    horizontal_axis = []
    i = 1
    for ab in outing.at_bats:
        for p in ab.pitches:
            horizontal_axis.append(i)
            i += 1

    velos = veloOverTime(outing)

    # render template with all the statistical data calculated from the outing
    return render_template(
        'outing/outing_stats_advanced.html',
        title=outing,
        outing=outing,
        opponent=opponent,
        pitch_stats=pitch_stats,
        time_to_plate=time_to_plate,
        labels=horizontal_axis,
        velos=velos
    )


@outing.route('/outing/<id>/stats/basic', methods=["GET", "POST"])
@login_required
def outing_stats_basic(id):

    outing = Outing.query.filter_by(id=id).first()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    return render_template(
        '/outing/outing_stats_basic.html',
        title=outing,
        outing=outing
    )


@outing.route('/outing/<id>/videos', methods=["GET", "POST"])
@login_required
def outing_videos(id):

    outing = Outing.query.filter_by(id=id).first()
    videos = Video.query.filter_by(outing_id=id).all()
    video_ids = []
    for v in videos:

        # https://gist.github.com/silentsokolov/f5981f314bc006c82a41
        # gets the id from a youtube linke
        regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
        match = regex.match(v.link)
        if not match:
            video_ids.append("")
        else:
            video_ids.append(match.group("id"))

    return render_template(
        '/outing/outing_videos.html',
        title=outing,
        outing=outing,
        video_objects=videos,
        videos=video_ids
    )

# ***************-NEW OUTING-*************** #
@outing.route('/new_outing', methods=['GET', 'POST'])
@login_required
def new_outing():
    '''
    NEW OUTING:
    Can create a new outing and pitches associated with
    that outing

    PARAM:
        -None

    RETURN:
        -new_outing.html allows user to enter in info for a
            specific outing and creates the outing object
            along with all the pitches objects associated
            with the outing
    '''
    form = OutingForm()

    # get list of all opponents so can limit # of pitchers visible
    teams = Opponent.query.all()

    # set the choices for all available pitchers
    form.pitcher.choices = getAvailablePitchers()

    # when the 'Create Outing' button is pressed
    if form.validate_on_submit():

        # gets the user associated the username of the pitcher the outing
        # is being created for
        # pitcher = Pitcher.query.filter_by(id=form.pitcher.data).first_or_404()

        # safety check for outing chosen
        if form.game.data is None:
            game_id = ""
        else:
            game_id = form.game.data.id

        # creates a new outing object based on form data and user
        outing = Outing(
            date=form.date.data,
            opponent_id=form.opponent.data.id,
            season_id=form.season.data.id,
            pitcher_id=form.pitcher.data,
            game_id=game_id
        )

        # add the new outing to the database before pitches so pitches have a
        # outing_id associated with them
        db.session.add(outing)
        db.session.commit()

        # redirects back to home page after outing was successfully created
        flash("New Outing Created!")
        return redirect(url_for('outing.new_outing_pitch_tracker', id=outing.id))

    return render_template('outing/new_outing.html',
                           title='New Outing',
                           form=form,
                           teams=teams)

# ***************-NEW OUTING PITCHES-*************** #
@outing.route('/new_outing_pitches/<outing_id>', methods=['GET', 'POST'])
@login_required
def new_outing_pitches(outing_id):

    # get the form associated with entering in X number of pitches
    form = OutingPitchForm()

    # set up batter choices
    for subform in form.pitch:
        subform.batter_id.choices = getAvailableBatters(outing_id)

    # get the outing/season associated with the id
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    season = Season.query.filter_by(id=outing.season_id).first_or_404()

    # if "add pitches" button was clicked
    if form.validate_on_submit():

        # sets up count for first pitch of outing
        if (season.semester == 'Fall'):
            balls = 1
            strikes = 1
            count = f'{balls}-{strikes}'
        else:
            balls = 0
            strikes = 0
            count = f'{balls}-{strikes}'

        # Boolean variable to help with adding AtBat objects to the database
        new_at_bat = True

        # variable to hold the current AtBat object
        current_at_bat = None

        # add each individual pitch to the database
        for index, subform in enumerate(form.pitch):

            # get the batter_id for the AtBat and Pitch objects
            batter_id = subform.batter_id.data

            # if a new at bat has started, make a new AtBat object
            if new_at_bat:
                at_bat = AtBat(
                    batter_id=batter_id,
                    outing_id=outing_id)

                # Add the AtBat object to database
                db.session.add(at_bat)
                db.session.commit()

                # Set the current_at_bat for subsequent pitches accordingly
                current_at_bat = at_bat

                # So new at_bat variables aren't made every pitch
                new_at_bat = False

            # sets the pitch_num column automatically
            pitch_num = index + 1

            # create Pitch object
            pitch = Pitch(
                atbat_id=current_at_bat.id,
                pitch_num=pitch_num,
                batter_id=batter_id,
                velocity=subform.velocity.data,
                lead_runner=subform.lead_runner.data,
                time_to_plate=subform.time_to_plate.data,
                pitch_type=subform.pitch_type.data,
                pitch_result=subform.pitch_result.data,
                hit_spot=subform.hit_spot.data,
                count=count,
                ab_result=subform.ab_result.data,
                traj=subform.traj.data,
                fielder=subform.fielder.data,
                inning=subform.inning.data)

            # update count based on current count and pitch result
            balls, strikes, count = updateCount(balls,
                                                strikes,
                                                pitch.pitch_result,
                                                pitch.ab_result,
                                                season)

            # adds pitch to database
            db.session.add(pitch)
            db.session.commit()

            # after the pitch was made, if the at_bat ended, reset variable
            # so a new at_bat starts during the next loop
            if pitch.ab_result is not '':
                new_at_bat = True

        flash('Pitches added to outing!')
        return redirect(url_for('outing.outing_home', id=outing_id))

    return render_template(
        'outing/new_outing_pitches.html',
        title='New Outing Pitches',
        form=form
    )

# ***************-EDIT OUTING PITCHES-*************** #
@outing.route('/edit_outing_pitches/<outing_id>', methods=['GET', 'POST'])
@login_required
def edit_outing_pitches(outing_id):
    '''
    EDIT OUTING PITCHES
    Can edit pitches of an existing outing

    PARAM:
        -outing_id: the outing id (primary key) in which the user
            wants to access

    RETURN:
        -edit_outing_pitches.html which allows user to edit the pitches of
            the outing requested. The function deletes the existing pitches
            and uploads the updated ones to the database.
    '''

    # get the database objects needed for the function
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    pitcher = Pitcher.query.filter_by(id=outing.pitcher_id).first_or_404()
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first_or_404()
    if outing.season_id not in [None, ""]:
        season = Season.query.filter_by(id=outing.season_id).first_or_404()
    else:
        season = None

    # only admins can go back and edit outing data
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('main.index'))

    # get the correct form
    form = OutingPitchForm()

    # set up batter choices here
    for subform in form.pitch:
        subform.batter_id.choices = getAvailableBatters(outing_id)

    # when edit wants to be made
    if form.validate_on_submit():

        # delete all of the pitches/at_bats associated with the outing
        for at_bat in outing.at_bats:
            for p in at_bat.pitches:
                db.session.delete(p)
            db.session.delete(at_bat)

        # commit the changes
        db.session.commit()

        # sets up count for first pitch of outing
        if season is not None:
            if season.semester == 'Fall':
                balls = 1
                strikes = 1
                count = f'{balls}-{strikes}'
            else:
                balls = 0
                strikes = 0
                count = f'{balls}-{strikes}'
        else:
            balls = 0
            strikes = 0
            count = f'{balls}-{strikes}'

        # Boolean variable to help with adding AtBat objects to the database
        new_at_bat = True

        # variable to hold the current AtBat object
        current_at_bat = None

        # add each individual pitch to the database
        for index, subform in enumerate(form.pitch):

            # get the batter_id for the AtBat and Pitch objects
            batter_id = subform.batter_id.data

            # if a new at bat has started, make a new AtBat object
            if new_at_bat:
                at_bat = AtBat(batter_id=batter_id,
                               outing_id=outing_id)

                # Add the AtBat object to database
                db.session.add(at_bat)
                db.session.commit()

                # Set the current_at_bat for subsequent pitches accordingly
                current_at_bat = at_bat

                # So new at_bat variables aren't made every pitch
                new_at_bat = False

            # sets the pitch_num column automatically
            pitch_num = index + 1

            # create Pitch object
            pitch = Pitch(atbat_id=current_at_bat.id,
                          pitch_num=pitch_num,
                          batter_id=batter_id,
                          velocity=subform.velocity.data,
                          lead_runner=subform.lead_runner.data,
                          time_to_plate=subform.time_to_plate.data,
                          pitch_type=subform.pitch_type.data,
                          roll_through=subform.roll_through.data,
                          short_set=subform.short_set.data,
                          pitch_result=subform.pitch_result.data,
                          hit_spot=subform.hit_spot.data,
                          count=count,
                          ab_result=subform.ab_result.data,
                          traj=subform.traj.data,
                          fielder=subform.fielder.data,
                          hit_hard=subform.hit_hard.data,
                          inning=subform.inning.data,
                          loc_x=subform.loc_x.data,
                          loc_y=subform.loc_y.data,
                          spray_x=subform.spray_x.data,
                          spray_y=subform.spray_y.data,
                          notes=subform.notes.data)

            # update count based on current count and pitch result
            balls, strikes, count = updateCount(balls,
                                                strikes,
                                                pitch.pitch_result,
                                                pitch.ab_result,
                                                season)

            # adds pitch to database
            db.session.add(pitch)
            db.session.commit()

            # after the pitch was made, if the at_bat ended, reset variable
            # so a new at_bat starts during the next loop
            if pitch.ab_result is not '':
                new_at_bat = True

        # redirect to outing page
        flash('The outing has been adjusted!')
        return redirect(url_for('outing.outing_home', id=outing.id))

    # sets up subforms so they are visible in edit_outing.html
    num_pitches = 0
    for at_bat in outing.at_bats:
        for pitch in at_bat.pitches:
            num_pitches += 1
    for p in range(1, num_pitches):
        form.pitch.append_entry()

    # set up batter choices here
    for subform in form.pitch:
        subform.batter_id.choices = getAvailableBatters(outing_id)

    batters = []
    for b in opponent.batters:
        batters.append(b)

    return render_template('outing/edit_outing_pitches.html',
                           title='Edit Outing',
                           outing=outing,
                           opponent=opponent,
                           form=form)

# ***************-EDIT OUTING-*************** #
@outing.route('/edit_outing/<outing_id>', methods=['GET', 'POST'])
@login_required
def edit_outing(outing_id):

    # get correct form
    form = OutingForm()

    # get the available pitchers to choose from
    form.pitcher.choices = getAvailablePitchers()

    # get objects from database
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    if not outing:  # Safety check
        flash("URL does not exist")
        return redirect(url_for('main.index'))

    opponent = Opponent.query.filter_by(id=outing.opponent_id).first_or_404()
    if outing.season_id in [None, ""]:
        this_season = None
    else:
        this_season = Season.query.filter_by(id=outing.season_id).first_or_404()
    all_seasons = Season.query.all()
    this_pitcher = Pitcher.query.filter_by(id=outing.pitcher_id).first_or_404()
    all_pitchers = Pitcher.query.all()
    # get the game currently selected and all selectable games
    if outing.game_id not in [None, ""]:
        this_game = Game.query.filter_by(id=outing.game_id).first_or_404()
    else:
        this_game = ""
    all_games = Game.query.all()

    # only admins can go back and edit outing data
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('main.index'))

    # when edit wants to be made
    if form.validate_on_submit():

        # get the user object from form
        pitcher = Pitcher.query.filter_by(id=form.pitcher.data).first()

        # update data for outing object
        outing.pitcher_id = pitcher.id
        outing.date = form.date.data
        outing.season_id = form.season.data.id

        # safety check for outing chosen
        if form.game.data is None:
            game_id = ""
        else:
            game_id = form.game.data.id

        # Update data for outing object game class
        outing.game_id = game_id

        # commit changes to database
        db.session.commit()

        # redirect to user page
        flash('The outing has been adjusted!')
        return redirect(url_for('pitcher.pitcher_home', id=pitcher.id))

    return render_template('outing/edit_outing.html',
                           title='Edit Outing',
                           outing=outing,
                           opponent=opponent,
                           this_season=this_season,
                           all_seasons=all_seasons,
                           this_pitcher=this_pitcher,
                           all_pitchers=all_pitchers,
                           this_game=this_game,
                           all_games=all_games,
                           form=form)

# ***************-DELETE OUTING-*************** #
@outing.route('/delete_outing/<id>', methods=['GET', 'POST'])
@login_required
def delete_outing(id):
    '''
    DELETE OUTING
    Can delete an existing outing through this function

    PARAM:
        -id: the outing id (primary key) in which the user
            wants to delete

    RETURN:
        -deletes the outing and redirects to user page which the outing
            was associated with
    '''

    # get the outing and user objects associated with this outing
    outing = Outing.query.filter_by(id=id).first_or_404()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))
    pitcher = Pitcher.query.filter_by(id=outing.pitcher_id).first_or_404()

    # only admins have permission to delete an outing
    if not current_user.admin:
        flash("You are not an admin and cannot edit someone else's outing")
        return redirect(url_for('main.index'))

    # deletes the pitches associated with outing
    for at_bat in outing.at_bats:
        for p in at_bat.pitches:
            db.session.delete(p)
        db.session.delete(at_bat)

    # deletes the outing iteself and commits changes to database
    db.session.delete(outing)
    db.session.commit()

    # redirects to user page associated with deletion
    flash('Outing has been deleted')
    return redirect(url_for('pitcher.pitcher_home', id=pitcher.id))


# ***************-NEW OUTING CSV-*************** #
@outing.route('/new_outing_csv', methods=['GET', 'POST'])
@login_required
def new_outing_csv():
    '''
    NEW OUTING CSV

    PARAM:
        -NONE

    RETURN:
        -
    '''

    form = NewOutingFromCSV()
    form.pitcher.choices = getAvailablePitchers()

    if form.validate_on_submit():

        # Get upload filename and save it to a temp file we can work with
        file_name = form.file.data.filename
        file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                "..",
                                "csv_files",
                                file_name)

        # save the file with its current name
        form.file.data.save(file_loc)

        # WIP make it so that duplicate file names dont appear
        # while os.path.isfile(file_loc):
        #     file_name = file_name + random.randint()

        # Analyze *.csv file for errors and discrepencies
        if validate_CSV(file_loc):

            # gets the user associated the username of the pitcher the outing
            # is being created for
            pitcher = Pitcher.query.filter_by(id=form.pitcher.data).first_or_404()

            # safety check for outing chosen
            if form.game.data is None:
                game_id = ""
            else:
                game_id = form.game.data.id

            # creates a new outing object based on form data and user
            outing = Outing(
                date=form.date.data,
                opponent_id=form.opponent.data.id,
                season_id=form.season.data.id,
                pitcher_id=pitcher.id,
                game_id=game_id)

            # add the new outing to the database before pitches so pitches
            # have a outing_id associated with them
            db.session.add(outing)
            db.session.commit()

            return redirect(url_for(
                'outing.new_outing_csv_pitches',
                file_name=file_name,
                outing_id=outing.id))
        else:  # delete invalid csv and refresh page
            os.remove(file_loc)
            flash("CSV given is invalid")
            return render_template("csv/upload_csv.html",
                                   form=form)

    return render_template("csv/upload_csv.html",
                           form=form)


# ***************-NEW OUTING CSV PITCHES-*************** #
@outing.route('/new_outing_csv_pitches/<file_name>/<outing_id>',methods=['GET', 'POST'])
@login_required
def new_outing_csv_pitches(file_name, outing_id):
    '''
    NEW OUTING CSV

    PARAM:
        -NONE

    RETURN:
        -
    '''
    # location of file name, passed from new_outing_csv via GET
    file_loc = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..",
        "csv_files",
        file_name)

    # extract pitches from CSV so they can be put in html form
    pitches = []
    with open(file_loc) as f:
        csv_file = csv.DictReader(f)
        for index, row in enumerate(csv_file):
            pitch = {
                "velocity": row['velocity'],
                "lead_runner": row['lead_runner'],
                "time_to_plate": row['time_to_plate'],
                "pitch_type": row['pitch_type'],
                "pitch_result": row['pitch_result'],
                "hit_spot": row['hit_spot'],
                "traj": row['traj'],
                "ab_result": row['ab_result'],
                "fielder": row['fielder'],
                "inning": row['inning']
            }
            if 'batter_id' in row.keys():
                pitch["batter_id"] = row["batter_id"]
            pitches.append(pitch)

    # Retrieve required DB objects
    outing = Outing.query.filter_by(id=outing_id).first_or_404()
    if not outing:
        flash("URL does not exist")
        return redirect(url_for('main.index'))
    pitcher = Pitcher.query.filter_by(id=outing.pitcher_id).first_or_404()
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first_or_404()
    season = Season.query.filter_by(id=outing.season_id).first_or_404()

    # Setup form and form variables
    form = NewOutingFromCSVPitches()
    # set up batter choices
    for subform in form.pitch:
        subform.batter_id.choices = getAvailableBatters(outing_id)
    # batter choices to fill into html
    batters = []
    for b in opponent.batters:
        batters.append(b)

    if form.validate_on_submit():

        # sets up count for first pitch of outing
        # sets up count for first pitch of outing
        if (season.semester == 'Fall'):
            balls = 1
            strikes = 1
        else:
            balls = 0
            strikes = 0
        count = f'{balls}-{strikes}'

        # Boolean variable to help with adding AtBat objects to the db
        new_at_bat = True

        # variable to hold the current AtBat object
        current_at_bat = None

        # add each individual pitch to the database
        for index, subform in enumerate(form.pitch):

            # get the batter_id for the AtBat and Pitch objects
            batter_id = subform.batter_id.data

            # if a new at bat has started, make a new AtBat object
            if new_at_bat:
                at_bat = AtBat(
                    batter_id=batter_id,
                    outing_id=outing_id)

                # Add the AtBat object to database
                db.session.add(at_bat)
                db.session.commit()

                # Set the current_at_bat for subsequent pitches accordingly
                current_at_bat = at_bat

                # So new at_bat variables aren't made every pitch
                new_at_bat = False

            # creates Pitch object based on subform data
            pitch_num = index + 1

            # create Pitch object
            pitch = Pitch(
                atbat_id=current_at_bat.id,
                pitch_num=pitch_num,
                batter_id=subform.batter_id.data,
                velocity=subform.velocity.data,
                lead_runner=subform.lead_runner.data,
                time_to_plate=subform.time_to_plate.data,
                pitch_type=subform.pitch_type.data,
                pitch_result=subform.pitch_result.data,
                hit_spot=subform.hit_spot.data,
                count=count,
                ab_result=subform.ab_result.data,
                traj=subform.traj.data,
                fielder=subform.fielder.data,
                inning=subform.inning.data)

            # update count based on current count and pitch result
            balls, strikes, count = updateCount(
                balls,
                strikes,
                pitch.pitch_result,
                pitch.ab_result,
                season)

            # adds pitch to database
            db.session.add(pitch)
            db.session.commit()

            if pitch.ab_result is not '':
                new_at_bat = True

        # delete temp file and be done with it
        os.remove(file_loc)

        flash("New Outing Created!")
        return redirect(url_for('main.index'))
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(err)

    return render_template("csv/new_outing_csv_pitches.html",
                           form=form,
                           pitches=pitches,
                           batters=batters)


@outing.route('/outing_report/<id>',methods=['GET', 'POST'])
@login_required
def outing_report(id):
    # get the outing object associated by the id in the url
    outing = Outing.query.filter_by(id=id).first()

    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('main.index'))

    # get opponent associated with outing
    opponent = Opponent.query.filter_by(id=outing.opponent_id).first()

    # if bug or outing trying to be viewed DNE
    if not outing:
        flash("URL does not exits")
        return redirect(url_for('main.index'))
    
    # Get statistical data
    pitch_stats = outingPitchStatistics(outing)
    time_to_plate = outingTimeToPlate(outing)

    pitch_usage_pie_labels = []
    pitch_usage_pie_data = []
    strike_percentage_polar_labels = []
    strike_percentage_polar_data = []
    for p in pitch_stats:
        pitch_usage_pie_labels.append(p['pitch_type'])
        strike_percentage_polar_labels.append(p['pitch_type'])
        if p['num_thrown'] in [0, None, "", "X", "x"]:
            pitch_usage_pie_data.append(0)
            strike_percentage_polar_data.append(0)
        else:
            pitch_usage_pie_data.append(p['num_thrown'])
            strike_percentage_polar_data.append(p['strike_percentage'])

    # setting up horizontal axis for line chart
    horizontal_axis = []
    i = 1
    for ab in outing.at_bats:
        for p in ab.pitches:
            horizontal_axis.append(i)
            i += 1

    velos = veloOverTime(outing)

    # render template with all the statistical data calculated from the outing
    return render_template(
        'outing/outing_report.html',
        title=outing,
        outing=outing,
        opponent=opponent,
        pitch_stats=pitch_stats,
        time_to_plate=time_to_plate,
        velos=velos,
        labels=horizontal_axis,
        pitch_usage_pie_data=pitch_usage_pie_data,
        pitch_usage_pie_labels=pitch_usage_pie_labels,
        strike_percentage_polar_labels=strike_percentage_polar_labels,
        strike_percentage_polar_data=strike_percentage_polar_data
    )


@outing.route('/new_outing_pitch_tracker/<id>', methods=['GET', 'POST'])
@login_required
def new_outing_pitch_tracker(id):
    
    outing = Outing.query.filter_by(id=id).first_or_404()

    # to hold all the pitches from outing to be displayed in table
    pitches = []

    # to hold the pitch count by inning
    pitch_count_inning = {
        "1": 0, "2": 0, "3": 0,
        "4": 0, "5": 0, "6": 0,
        "7": 0, "8": 0, "9": 0,
        "10": 0, "11": 0, "12": 0
    }

    # for count and pitch count totals
    num_pitches = 0
    balls = 0
    strikes = 0

    inning = 1

    # to know whether to reset at bat
    current_at_bat = ""

    # in case of in middle of at bat
    current_batter = ""
    lead_runner = ""

    # for inning data on chart
    inning_totals = {}
    inning_data_table = {}
    for i in range(1,10):
        inning_totals[i] = {"pitches": 0, "pitches_with_velo": 0, "velo_total": 0, "num_strikes": 0}
        inning_data_table[i] = {"pitches": 0, "velo": 0, "strike_pct": 0}
    inning_totals["Totals"] = {"pitches": 0, "pitches_with_velo": 0, "velo_total": 0, "num_strikes": 0}
    inning_data_table["Totals"] = {"pitches": 0, "velo": 0, "strike_pct": 0}

    # looks through all pitches and set variables accordingly
    for at_bat in outing.at_bats:

        # set the current at bat (last one is the only one that matters)
        current_at_bat = at_bat.id

        for p in at_bat.pitches:

            num_pitches += 1

            pitch_count_inning[f"{p.inning}"] += 1

            # add pitch to array
            pitch = {
                "batter_id": p.batter_id,
                "velocity": p.velocity,
                "lead_runner": p.lead_runner,
                "time_to_plate": p.time_to_plate,
                "pitch_type": p.pitch_type,
                "roll_through": p.roll_through,
                "short_set": p.short_set,
                "pitch_result": p.pitch_result,
                "loc_x": p.loc_x,
                "loc_y": p.loc_y,
                "hit_spot": p.hit_spot,
                "ab_result": p.ab_result,
                "traj": p.traj,
                "fielder": p.fielder,
                "spray_x": p.spray_x,
                "spray_y": p.spray_y,
                "hit_hard": p.hit_hard,
                "inning": p.inning,
                "notes": p.notes
            }   
            pitches.append(pitch)

            # update data for inning data table
            inning_totals[p.inning]["pitches"] += 1
            inning_totals["Totals"]["pitches"] += 1
            if p.pitch_type in [1,"1",7,"7"]:
                if p.velocity not in ["", None]:
                    inning_totals[p.inning]["pitches_with_velo"] += 1
                    inning_totals["Totals"]["pitches_with_velo"] += 1
                    inning_totals[p.inning]["velo_total"] += p.velocity
                    inning_totals["Totals"]["velo_total"] += p.velocity
            if p.pitch_result is not "B":
                inning_totals[p.inning]["num_strikes"] += 1
                inning_totals["Totals"]["num_strikes"] += 1

            # update count based on pitch result
            count = p.count.split("-")
            balls = int(count[0])
            strikes = int(count[1])
            if p.pitch_result == "B":
                balls += 1
            elif p.pitch_result == "F" and strikes == 2:
                strikes = 2
            else:
                strikes += 1

            # send the current_batter back to tracker
            current_batter = p.batter_id
            lead_runner = p.lead_runner
            inning = p.inning

            # if the at bat was over, alter variables
            if p.ab_result != "":
                balls = 0
                strikes = 0
                current_at_bat = ""
                current_batter = ""
                lead_runner = ""

    # calculate averages and strike percentage
    for key in inning_totals:
        inning_data_table[key]["pitches"] = inning_totals[key]["pitches"]
        if inning_totals[key]["pitches_with_velo"] != 0:
            inning_data_table[key]["velo"] = truncate(inning_totals[key]["velo_total"]/inning_totals[key]["pitches_with_velo"])
        if inning_totals[key]["pitches"] != 0:
            inning_data_table[key]["strike_pct"] = percentage(inning_totals[key]["num_strikes"]/inning_totals[key]["pitches"])

    # clean up pitch data info for javascript
    for key, val in enumerate(pitches):
        if val in ["", None]:
            pitches[key] = ""
        elif val == True:
            pitches[key] = 1
        elif val == False:
            pitches[key] = 0
        else:
            pitches[key] = val

    # set the batters associated with the opponent
    batters = Batter.query.filter_by(opponent_id=outing.opponent_id).filter_by(retired = 0).order_by(Batter.number).all()

    return render_template(
        "outing/pitch_tracker/new_outing_pitch_tracker.html",
        batters=batters,
        outing=outing,
        pitches=pitches,
        num_pitches=num_pitches,
        pitch_count_inning=pitch_count_inning,
        balls=balls,
        strikes=strikes,
        at_bat=current_at_bat,
        batter=current_batter,
        inning=inning,
        lead_runner=lead_runner,
        inning_data_table=inning_data_table
    )


# ***************-HELPFUL FUNCTIONS-*************** #
def truncate(n, decimals=1):
    """Truncates the passed value to decimal places.

    Arguments:
        n {number} -- Number to be truncated

    Keyword Arguments:
        decimals {int} -- Number of decimal places to truncate to(default: {2})

    Returns:
        [int] -- truncated verison of passed value
    """
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def percentage(n, decimals=0):
    '''
    Gets the percentage rounded to a specific decimal place
    PARAM:
        - n - is a the decimal number 0<=n<=1
        - decimals - is the place you want to round to
    '''
    multiplier = 10 ** decimals
    percentage = 100 * n
    return int(math.floor(percentage*multiplier + 0.5) / multiplier)


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


def validate_CSV(file_loc):
    '''
    Validates an uploaded outing csv file to see if we can create pitches
    from it.

    PARAM:
        -file_loc {string} -- string location of the file to be validated

    RETURN:
        [boolean] -- boolean for if the file is determined valid
    '''

    # fields required to construct a pitch from Pitch class in modals. We need
    # to check if all of these exist.
    pitch_attributes = [
        "velocity", "lead_runner", "time_to_plate", "pitch_type",
        "pitch_result", "hit_spot", "ab_result", "traj", "fielder",
        "inning"]
    with open(file_loc) as f:

        csv_file = csv.DictReader(f)
        invalid_pitch_found = False  # State var to see if pitches are valid

        for pitch_num, row in enumerate(csv_file):
            keys = row.keys()

            # Check if the our necessary keys is contained within the csv
            # keys provided.
            if set(pitch_attributes).issubset(set(keys)):
                print("You have the necessary keys")

            else:
                invalid_pitch_found = True

                # Debug statement. Eventually move to user facing so they can
                # adjust input.
                for attr in pitch_attributes:
                    if attr not in keys:
                        print(f"Pitch num {pitch_num} missing {attr}")
                break

        if invalid_pitch_found:
            return False
        else:
            return True


def updateCount(balls, strikes, pitch_result, ab_result, season):
    if ab_result is not '':
        if season is not None:
            if (season.semester == 'Spring' and season.year == "2020"):
                balls = 0
                strikes = 0
            elif season.semester == 'Fall':
                balls = 1
                strikes = 1
            else:
                balls = 0
                strikes = 0
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
