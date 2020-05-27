from app import db

from flask import flash
from flask import url_for
from flask import request
from flask import redirect
from flask import Blueprint
from flask import render_template

from app.models import Resource

from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

from app.forms import NewResourceForm 

resource = Blueprint("resource", __name__)

# TEMPLATES
@resource.route('/new_resource', methods=['GET', 'POST'])
@login_required
def new_resource():
    return render_template(
        "resource/new_resource.html",
        title="New Resource",
        form=NewResourceForm()
    )

# CRUD
# create
@resource.route('/resource', methods=['POST'])
def add_resource():
    '''API Route to create a new resource
    Only thing that could be added here is url validation for the articles or videos, 
        but that is done on the front end (form) side

    Requst Args:
        category (required): Pitching, Hitting, Defense, Mental Game, or Miscellaneous
        title (required): The title of the resource,
        description (optional): The description for the resource
        Exactly one of the next three must be present:
            article_link: a valid url
            video_link: a valid youtube url to a video
            file: a pdf file 
    Returns:
        HTML based on the request and whether it was successfull or not
    '''
    # Make sure form data exists in request
    if request.form:
        form_data = request.form
    else:
        flash('Invalid request. No form data present')
        return redirect(url_for('main.index')) 
    
    # Filter string form params to make sure everything is valid
    params = {'category': '', 'title': '', 'description': '', 'article_link': '', 'video_link': ''}
    required_params = ['category', 'title']
    for param in params.keys():
        if param in form_data:
            params[param] = form_data[param]
        else:
            if param in required_params:
                flash(f'Invalid request. No {param} present')
                return redirect(url_for('main.index'))            

    # Check for file in request
    file_data = None
    if 'file' in request.files:
        file_data = request.files['file'].read()
    
    # Only one of three params must be present: article_line, video_link, file_data
    if not params['article_link']:
        if not params['video_link']:
            if not file_data:
                flash('Invalid request. Need a youtube/article link or PDF file')
                return redirect(url_for('main.index'))
        else:
            if file_data:
                flash('Invalid request. Only one resource type must be provided')
                return redirect(url_for('main.index'))
    else:
        if params['video_link'] or file_data:
            flash('Invalid request. Only one resource type must be provided')
            return redirect(url_for('main.index'))

    # If all goes well above, add the resource to the database
    resource = Resource(
        category=params['category'],
        title=params['title'],
        description=params['description'],
        article_link=params['article_link'],
        video_link=params['video_link'],
        file_data=file_data
    )
    db.session.add(resource)
    db.session.commit()
    return redirect(url_for('resource.new_resource'))
