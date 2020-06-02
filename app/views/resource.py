from app import db

from flask import flash
from flask import url_for
from flask import request
from flask import redirect
from flask import Blueprint
from flask import render_template
from flask import jsonify

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
def create_resource():
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
    file_data = read_file_from_request(request, 'file')
    
    # Only one of three params must be present: article_line, video_link, file_data
    if not exactly_one_param_present(params['article_link'], params['video_link'], file_data):
        flash('Invalid request. Need exactly one of: article link, video link, file')
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
    return redirect(url_for('main.index'))

@resource.route('/resource', methods=['GET'])
def read_resource():
    # Gather data from query string params
    category = request.args.get('category')
    resource_type = request.args.get('resource_type')

    # this will be where query is held
    query = 'Resource.query'

    # look at request params and setup query based on them
    if resource_type in ['article', 'article_link', 'Article']:
        resource_type = 'article'
        query += f".filter(Resource.article_link != '')"
    if resource_type in ['youtube', 'YouTube', 'video', 'Video', 'video_link']:
        resource_type = 'video'
        query += f".filter(Resource.video_link != '')"
    if resource_type in ['file', 'file_data', 'pdf', 'PDF', 'File']:
        resource_type = 'file'
        query += f".filter(Resource.file_data != None)"
    
    if category in ['Pitching', 'pitching', 'pitchers', 'Pitchers']:
        category = 'Pitching'
    if category in ['Hitting', 'hitting', 'hitters', 'Hitters']:
        category = 'Hitting'
    if category in ['Defense', 'defense', 'fielding', 'fielders', 'Fielding']:
        category = 'Defense'
    if category in ['Mental Game', 'Mental', 'mental game', 'mental']:
        category = 'Mental Game'
    if category in ['Miscellaneous', 'miscellaneous', 'Other', 'other']:
        category = 'Miscellaneous'

    if category:
        query += f".filter_by(category = '{category}')"

    query += '.all()'

    resources = eval(query)
    return_resources = []
    for resource in resources:
        return_resources.append(resource.to_dict())
    print(return_resources)
    return 'hey'
    # return jsonify(return_resources)
    
# update
@resource.route('/resource/<id>', methods=['PATCH'])
def update_resource(id):
    '''API Route to update a resource
    The update will take the exact form of the request, so if something doesn't need to
    be updated, it still needs to be passed as form data.

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

    # Check to make sure resource exists
    resource = Resource.query.filter_by(id=id).first()
    if not resource:
        flash('Invalid request. ID passed does not match any resource')
        return redirect(url_for('main.index'))
    
    # Check to make sure form data was present in request
    if not request.form:
        flash('Invalid request. No form data present')
        return redirect(url_for('main.index'))
    form_data = request.form

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
    file_data = read_file_from_request(request, 'file')
    
    # Only one of three params must be present: article_line, video_link, file_data
    if not exactly_one_param_present(params['article_link'], params['video_link'], file_data):
        flash('Invalid request. Need exactly one of: article link, video link, file')
        return redirect(url_for('main.index'))

    # Update the resource based on everything passed through
    resource.category = params['category']
    resource.title = params['title']
    resource.description = params['description']
    resource.article_link = params['article_link']
    resource.video_link = params['video_link']
    resource.file_data = file_data

    db.session.commit()
    return redirect(url_for('main.index'))

# delete
@resource.route('/resource/<id>', methods=['DELETE'])
def delete_resource(id):
    '''API Route to delete a resource by its id

    Requst Args:
        The id in the url such as /resource/4 to delete the resource with id=4
    Returns:
        HTML based on the request and whether it was successfull or not
    '''
    resource = Resource.query.filter_by(id=id).first()
    if not resource:
        flash('Invalid request. ID passed does not match any resource')
        return redirect(url_for('main.index'))

    db.session.delete(resource)
    db.session.commit()
    return redirect(url_for('main.index'))

# UTIL FUNCTIONS
def exactly_one_param_present(one, two, three):
    number_present = 0
    if one:
        number_present += 1
    if two:
        number_present += 1
    if three:
        number_present += 1
    return number_present == 1

def read_file_from_request(request, file_name):
    if file_name in request.files:
        return request.files[file_name].read()
    return None

