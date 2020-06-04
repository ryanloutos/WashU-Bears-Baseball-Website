from app import db

from flask import flash
from flask import url_for
from flask import request
from flask import redirect
from flask import Blueprint
from flask import render_template
from flask import jsonify
from flask import send_from_directory

from flask_api import status

from app.models import Resource

from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

from app.forms import NewResourceForm 

import os

resource = Blueprint("resource", __name__)

# ***************-TEMPLATES-*************** #
@resource.route('/new_resource', methods=['GET'])
@login_required
def new_resource():
    return render_template(
        'resource/new_resource.html',
        title='New Resource',
        form=NewResourceForm()
    )

@resource.route('/resource/home', methods=['GET'])
@login_required
def resource_home():
    return render_template(
        'resource/resources_home.html',
        title='Team Resources',
    )

@resource.route('/resource/pitching', methods=['GET'])
@login_required
def pitching_resources():
    return render_template(
        'resource/pitching_resources.html',
        title='Pitching Resources',
    )

@resource.route('/resource/hitting', methods=['GET'])
@login_required
def hitting_resources():
    return render_template(
        'resource/hitting_resources.html',
        title='Hitting Resources',
    )

@resource.route('/resource/defense', methods=['GET'])
@login_required
def defense_resources():
    return render_template(
        'resource/defense_resources.html',
        title='Defense Resources',
    )

@resource.route('/resource/mental_game', methods=['GET'])
@login_required
def mental_game_resources():
    return render_template(
        'resource/mental_game_resources.html',
        title='Mental Game Resources',
    )

@resource.route('/resource/miscellaneous', methods=['GET'])
@login_required
def miscellaneous_resources():
    return render_template(
        'resource/miscellaneous_resources.html',
        title='Miscellaneous Resources',
    )

@resource.route("/resource/download/<id>")
@login_required
def download_resource(id):
    resource = Resource.query.filter_by(id=id).first()
    if not resource or not resource.file_path:
        return send_from_directory(
            "static", "files/resources/file_does_not_exist.pdf",
            as_attachment=True,
            mimetype="application/pdf",
            attachment_filename="file_does_not_exist.pdf"
        )

    return send_from_directory(
        "static", resource.file_path,
        as_attachment=True,
        mimetype="application/pdf",
        attachment_filename=f"{resource.title}.pdf")

# ***************-CRUD API OPERATIONS-*************** #
# create
@resource.route('/resource', methods=['POST'])
@login_required
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
        A status code with a message
    '''
    # Make sure form data exists in request
    message = ''
    if not request.form:
        message = 'No form data present in request'
        return message, status.HTTP_400_BAD_REQUEST
    form_data = request.form
    
    # Filter string form params to make sure everything is valid
    params = {'category': '', 'title': '', 'description': '', 'article_link': '', 'video_link': ''}
    required_params = ['category', 'title']
    for param in params.keys():
        if param in form_data:
            params[param] = form_data[param]
        else:
            if param in required_params:
                message = f'Invalid request. No {param} present'
                return message, status.HTTP_400_BAD_REQUEST
    
    # Check to make sure title doesn't exist
    resources_with_same_title = Resource.query.filter_by(title=params['title']).filter_by(category=params['category']).all()
    if resources_with_same_title:
        message = 'There already exists a resource in that category with that title'
        return message, status.HTTP_400_BAD_REQUEST

    # Check for file in request
    file_path = save_file_to_file_system(request, 'file', params['title'])
    if file_path == 'Error':
        message = 'There was an error while saving the file'
        return message, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Only one of three params must be present: article_line, video_link, file_data
    if not exactly_one_param_present(params['article_link'], params['video_link'], file_path):
        message = f'Invalid request. Need exactly one of: article link, video link, file'
        return message, status.HTTP_400_BAD_REQUEST

    # If all goes well above, add the resource to the database
    resource = Resource(
        category=params['category'],
        title=params['title'],
        description=params['description'],
        article_link=params['article_link'],
        video_link=params['video_link'],
        file_path=file_path
    )
    db.session.add(resource)
    db.session.commit()
    return message, status.HTTP_200_OK

# read
@resource.route('/resource', methods=['GET'])
@login_required
def read_resource():
    '''API Route to read resources based on query strings

    Query String Params:
        - category (optional): the category of resources you want to get
        - resource_type (optional): file, video, or article
        
    Returns:
        An array of resources based on the query string params. Will return all resources
        if no params are given

    '''
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
    if resource_type in ['file', 'pdf', 'PDF', 'File']:
        resource_type = 'file'
        query += f".filter(Resource.file_path != None)"
    
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

    # query database and return an array of resources
    resources = eval(query)
    return_resources = []
    for resource in resources:
        return_resources.append(resource.to_dict())

    return jsonify(return_resources), status.HTTP_200_OK
    
# update
@resource.route('/resource/<id>', methods=['PATCH'])
@login_required
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
    message = ''
    resource = Resource.query.filter_by(id=id).first()
    if not resource:
        message = 'Invalid request. ID passed does not match any resource'
        return message, status.HTTP_400_BAD_REQUEST
    
    # Check to make sure form data was present in request
    if not request.form:
        message = 'No form data present in request'
        return message, status.HTTP_400_BAD_REQUEST
    form_data = request.form

    # Filter string form params to make sure everything is valid
    params = {'category': '', 'title': '', 'description': '', 'article_link': '', 'video_link': ''}
    required_params = ['category', 'title']
    for param in params.keys():
        if param in form_data:
            params[param] = form_data[param]
        else:
            if param in required_params:
                message = f'Invalid request. No {param} present'
                return message, status.HTTP_400_BAD_REQUEST          

    # Check for file in request
    if file_exists(resource.file_path):
        os.remove(resource.file_path)
    file_path = save_file_to_file_system(request, 'file', params['title'])
    if file_path == 'Error':
        message = 'There was an error while saving the file'
        return message, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Only one of three params must be present: article_line, video_link, file_data
    if not exactly_one_param_present(params['article_link'], params['video_link'], file_path):
        message = f'Invalid request. Need exactly one of: article link, video link, file'
        return message, status.HTTP_400_BAD_REQUEST

    # Update the resource based on everything passed through
    resource.category = params['category']
    resource.title = params['title']
    resource.description = params['description']
    resource.article_link = params['article_link']
    resource.video_link = params['video_link']
    resource.file_path = file_path

    db.session.commit()
    return message, status.HTTP_200_OK

# delete
@resource.route('/resource/<id>', methods=['DELETE'])
@login_required
def delete_resource(id):
    '''API Route to delete a resource by its id

    Requst Args:
        The id in the url such as /resource/4 to delete the resource with id=4
    Returns:
        HTML based on the request and whether it was successfull or not
    '''
    message = ''
    # check to make sure the resource exists
    resource = Resource.query.filter_by(id=id).first()
    if not resource:
        message = 'Invalid request. ID passed does not match any resource'
        return message, status.HTTP_400_BAD_REQUEST
    
    # delete the file if the resource is a file
    if file_exists(resource.file_path):
        os.remove(resource.file_path)

    db.session.delete(resource)
    db.session.commit()
    return message, status.HTTP_200_OK

# ***************-UTIL FUNCTIONS-*************** #
def exactly_one_param_present(one, two, three):
    number_present = 0
    if one:
        number_present += 1
    if two:
        number_present += 1
    if three:
        number_present += 1
    return number_present == 1

def save_file_to_file_system(request, file_name_in_request, file_name):
    if file_name_in_request in request.files:
        if not request.files[file_name_in_request].filename == '':
            file_loc = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "static",
                "files",
                "resources",
                f"{file_name}.pdf"
            )
            if not file_exists(file_loc):
                request.files[file_name_in_request].save(file_loc)
                return f'files/resources/{file_name}.pdf'
            else:
                extra_text_for_file_name = 1
                while file_exists(file_loc):
                    file_loc = os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        "..",
                        "static",
                        "files",
                        "resources",
                        f"{file_name}{extra_text_for_file_name}.pdf"
                    )
                    extra_text_for_file_name += 1
                    if extra_text_for_file_name == 10:
                        return 'Error'
                request.files[file_name_in_request].save(file_loc)
                return f'files/resources/{file_name}{extra_text_for_file_name}.pdf'
    return None

def file_exists(file_path):
    try:
        if not file_path:
            return False
        open(file_path)
        return True
    except IOError:
        return False
