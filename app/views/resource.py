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
from app.models import User

from flask_login import current_user
from flask_login import login_required

from app.forms import NewResourceForm
from app.forms import EditResourceForm

from app.emails import send_email

import os

resource = Blueprint("resource", __name__)

# ***************-TEMPLATES-*************** #
@resource.route('/new_resource', methods=['GET'])
@login_required
def new_resource():
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('resource.resource_home'))

    return render_template(
        'resource/new_resource.html',
        title='New Resource',
        form=NewResourceForm()
    )


@resource.route('/edit_resource/<id>', methods=['GET'])
@login_required
def edit_resource(id):
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('resource.resource_home'))

    resource = Resource.query.filter_by(id=id).first()
    if not resource:
        flash('URL does not exist')
        return redirect(url_for('resource.resource_home'))

    return render_template(
        'resource/edit_resource.html',
        resource=resource,
        title='Edit Resource',
        form=EditResourceForm()
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


@resource.route('/resource/program_playbook', methods=['GET'])
@login_required
def program_playbook_resources():
    return render_template(
        'resource/program_playbook_resources.html',
        title='Program Playbook Resources',
    )


@resource.route('/resource/plays_signs_strategy', methods=['GET'])
@login_required
def plays_signs_strategy_resources():
    return render_template(
        'resource/plays_signs_strategy_resources.html',
        title='Plays, Signs, & Strategy Resources',
    )


@resource.route('/resource/download/<id>')
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

    try:
        print(resource.file_path)
        filename = resource.file_path.split('/')
        return send_from_directory(
            "static", resource.file_path,
            as_attachment=True,
            attachment_filename=filename[2])

    except:
        return send_from_directory(
            "static", "files/resources/file_does_not_exist.pdf",
            as_attachment=True,
            mimetype="application/pdf",
            attachment_filename="file_does_not_exist.pdf"
        )


@resource.route('/resource/email', methods=['GET'])
@login_required
def new_resource_email():
    if not current_user.admin:
        flash("Admin feature only")
        return redirect(url_for('resource.resource_home'))

    # get the query params
    include_infielders = request.args.get('infielders')
    include_outfielders = request.args.get('outfielders')
    include_pitchers = request.args.get('pitchers')
    include_coaches = request.args.get('coaches')
    title = request.args.get('title')
    description = request.args.get('description')

    # make sure the email should be sent to either or both coaches and players
    true_list = ['True', 'true', 'TRUE']
    if (include_infielders not in true_list and
        include_outfielders not in true_list and
        include_pitchers not in true_list and
            include_coaches not in true_list):
        return "Set 'players' or 'coaches' equal to 'true'", status.HTTP_400_BAD_REQUEST

    # make sure a title is present to send the email
    if not title:
        return "Missing 'title' query param for the resource", status.HTTP_400_BAD_REQUEST

    # set up the email list of players/coaches
    email_list = set()
    if include_infielders:
        infielders = User.query.filter_by(infielder=1).all()
        for player in infielders:
            email_list.add(player.email)
    if include_outfielders:
        outfielders = User.query.filter_by(outfielder=1).all()
        for player in outfielders:
            email_list.add(player.email)
    if include_pitchers:
        pitchers = User.query.filter_by(pitcher=1).all()
        for player in pitchers:
            email_list.add(player.email)
    if include_coaches:
        team_coaches = User.query.filter_by(current_coach=1).all()
        for coach in team_coaches:
            email_list.add(coach.email)

    # set up basic message requirements
    subject = 'Check out the new resource just uploaded!'
    sender = 'Bears Baseball'
    html = ''

    # set up the body of the email
    message = f'Title: {title}\n'
    if description:
        message += f'Description: {description}\n\n'
    message += f'\nYou can check it out at bearsbaseball.pythonanywhere.com/resource/home'

    send_email(subject, sender, list(email_list), message, html)
    return 'success', status.HTTP_200_OK


# ***************-CRUD API OPERATIONS-*************** #
@resource.route('/resource', methods=['POST'])
def create_resource():
    try:
        data = {}
        file_path = ''

        # convert all empty string fields to None for SQL validation
        for field in ['category', 'title', 'description', 'resource_type', 'link']:
            if request.form[field] == '':
                data[field] = None
            else:
                data[field] = request.form[field]

        # Check to make sure title doesn't exist
        resources_with_same_title = Resource.query.filter_by(
            title=data['title']).filter_by(category=data['category']).all()
        if resources_with_same_title:
            return 'Please give the resource a different title', status.HTTP_400_BAD_REQUEST

        # save the file if the resource type is a file
        if data['resource_type'] == 'file':
            file_path = save_file(request, 'file')

        # add resource to db
        db.session.add(Resource(
            category=data['category'],
            title=data['title'],
            description=data['description'],
            resource_type=data['resource_type'].lower(),
            link=data['link'],
            file_path=file_path
        ))
        db.session.commit()

        return '', status.HTTP_201_CREATED

    except Exception as e:
        print('Create Resource', e)
        delete_file(file_path)
        return '', status.HTTP_400_BAD_REQUEST


@resource.route('/resource', methods=['GET'])
@login_required
def read_resource():
    # Gather data from query string params
    category = request.args.get('category')
    resource_type = request.args.get('resource_type')
    recent = request.args.get('recent')

    # this will be where query is held
    query = 'Resource.query'

    # look at request params and setup query based on them
    if resource_type:
        query += f".filter_by(resource_type = '{resource_type}')"
    if category:
        query += f".filter_by(category = '{category}')"

    query += '.order_by(Resource.timestamp.desc()).all()'

    # query database and return an array of resources
    resources = eval(query)
    return_resources = []
    index = 0
    for resource in resources:
        if recent == 'true':
            if index < 4:
                return_resources.append(resource.to_dict())
        else:
            return_resources.append(resource.to_dict())
        index += 1

    return jsonify(return_resources), status.HTTP_200_OK


@resource.route('/resource/<id>', methods=['PATCH'])
@login_required
def update_resource(id):
    # Check to make sure resource exists
    resource = Resource.query.filter_by(id=id).first()
    if not resource:
        return '', status.HTTP_404_NOT_FOUND

    try:
        data = {}
        file_path = resource.file_path
        new_file = False

        # convert all empty string fields to None for SQL validation
        for field in ['category', 'title', 'description', 'resource_type', 'link']:
            if field in request.form.keys():
                if request.form[field] == '':
                    data[field] = None
                else:
                    data[field] = request.form[field]

        # Check to make sure title doesn't exist
        resources_with_same_title = Resource.query.filter_by(
            title=data['title']).filter_by(category=data['category']).all()
        if resources_with_same_title and resource.title != data['title']:
            return 'Please give the resource a different title', status.HTTP_400_BAD_REQUEST

        # save the file if the resource type is a file
        if 'resource_type' in request.form.keys():
            if data['resource_type'] == 'file' and request.files['file']:
                delete_file(resource.file_path)
                file_path = save_file(request, 'file')
                new_file = True

        # Update the resource based on everything passed through
        resource.category = data['category']
        resource.title = data['title']
        resource.description = data['description']
        if 'link' in request.form.keys():
            resource.link = data['link']
        if 'resource_type' in request.form.keys():
            resource.resource_type = data['resource_type']
        resource.file_path = file_path

        db.session.commit()
        return '', status.HTTP_200_OK

    except Exception as e:
        print('Update Resource', e)
        if new_file:
            delete_file(file_path)
        return '', status.HTTP_400_BAD_REQUEST


@resource.route('/resource/<id>', methods=['DELETE'])
@login_required
def delete_resource(id):
    # check to make sure the resource exists
    resource = Resource.query.filter_by(id=id).first()
    if not resource:
        return '', status.HTTP_404_NOT_FOUND

    try:
        # delete the file if the resource is a file
        if resource.resource_type == 'file':
            delete_file(resource.file_path)

        db.session.delete(resource)
        db.session.commit()

        return '', status.HTTP_200_OK

    except Exception as e:
        print('Delete Resource', e)
        return '', status.HTTP_500_INTERNAL_SERVER_ERROR


# ***************-UTIL FUNCTIONS-*************** #
def exactly_one_param_present(one, two, three):
    '''
    Checks the three params and returns true if exactly one of them exist
    '''
    number_present = 0
    if one:
        number_present += 1
    if two:
        number_present += 1
    if three:
        number_present += 1
    return number_present == 1


def delete_file(file_path):
    try:
        file_loc = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "static",
            file_path
        )
        if file_exists(file_loc):
            os.remove(file_loc)
    except Exception as e:
        print(e)


def save_file(request, file_name):
    try:
        file_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "static",
            "files",
            "resources",
            request.files[file_name].filename
        )
        relative_path = f'files/resources/{request.files[file_name].filename}'

        extra_text = 1
        while file_exists(file_path):
            file_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "static",
                "files",
                "resources",
                f'{extra_text}{request.files[file_name].filename}'
            )
            relative_path = f'files/resources/{extra_text}{request.files[file_name].filename}'
            extra_text += 1

        request.files[file_name].save(file_path)
        return relative_path

    except Exception as e:
        raise e
        return None


def file_exists(file_path):
    '''
    Returns True if the file exists for the path given, False otherwise
    '''
    try:
        if not file_path:
            return False
        open(file_path)
        return True
    except IOError:
        return False
