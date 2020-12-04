import os
import PIL

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)

from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from werkzeug.utils import secure_filename

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Birth, Image, Person, User
from cisca_admin.helpers import allowed_file

bp = Blueprint('index', __name__)

SEARCH_CRITERIA = ['Nickname', 'First name', 'Family name',
                   'First and family name', 'Find everyone!']


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'POST':
        criteria = request.form.get('criteria')
        return render_template('data/find.html', criteria=criteria, search_criteria=SEARCH_CRITERIA)

    return render_template('data/index.html', search_criteria=SEARCH_CRITERIA)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        nickname = '' if not request.form.get('nickname') \
            else request.form.get('nickname').lower()
        first_name = '' if not request.form.get('first_name') \
            else request.form.get('first_name').lower()
        middle_name = '' if not request.form.get('middle_name') \
            else request.form.get('middle_name').lower()
        family_name = '' if not request.form.get('family_name') \
            else request.form.get('family_name').lower()
        birth_year = request.form.get('birth_year')
        birth_month = request.form.get('birth_month')
        birth_day = request.form.get('birth_day')
        message = None

        if not first_name:
            message = 'First name is required.'

        if not family_name:
            message = 'Family name is required.'

        query = Person.query.filter(and_(
            Person.first_name == first_name,
            Person.family_name == family_name))

        if query.first() is not None:
            message = f'I already have a person named {first_name.capitalize()} {last_name.capitalize()}. Are you sure you want to create another one?'

        if message is None:
            new_person = Person(first_name=first_name, middle_name=middle_name,
                                family_name=family_name, nickname=nickname)
            new_person.birth = Birth(
                birth_year=birth_year, birth_month=birth_month, birth_day=birth_day)
            db_session.add(new_person)
            db_session.commit()

            message = f'{first_name.capitalize()} is created.'

        flash(message)

    return render_template('data/create.html')


@bp.route('/edit', methods=('GET', 'POST'))
@login_required
def edit():
    if request.method == 'POST':
        person_id = request.args.get('person_id')
        print(f'person_id in edit view: {person_id}')
        nickname = request.form.get('nickname').lower()
        first_name = request.form.get('first_name').lower()
        middle_name = request.form.get('middle_name').lower()
        family_name = request.form.get('family_name').lower()
        birth_year = request.form.get('birth_year')
        birth_month = request.form.get('birth_month')
        birth_day = request.form.get('birth_day')
        message = None

        if not first_name:
            message = 'First name is required.'

        if not family_name:
            message = 'Family name is required.'

        if message is None:
            query = Person.query.options(selectinload(Person.birth)).filter(
                Person.person_id == person_id).first()

            if query.nickname != nickname:
                flash(
                    f'Nickname {query.nickname.capitalize()} changed to {nickname.capitalize()}.')
                query.nickname = nickname
            if query.first_name != first_name:
                flash(
                    f'First name {query.first_name.capitalize()} changed to {first_name.capitalize()}.')
                query.first_name = first_name
            if query.middle_name != middle_name:
                flash(
                    f'Middle name {query.middle_name.capitalize()} changed to {middle_name.capitalize()}.')
                query.middle_name = middle_name
            if query.family_name != family_name:
                flash(
                    f'Family name {query.family_name.capitalize()} changed to {family_name.capitalize()}.')
                query.family_name = family_name
            if query.birth.birth_year != birth_year:
                flash(
                    f'Birth year {query.birth.birth_year} changed to {birth_year}.')
                query.birth.birth_year = birth_year
            if query.birth.birth_month != birth_month:
                flash(
                    f'Birth month {query.birth.birth_month} changed to {birth_month}.')
                query.birth.birth_month = birth_month
            if query.birth.birth_day != birth_day:
                flash(
                    f'Birthday {query.birth.birth_day} changed to {birth_day}.')
                query.birth.birth_day = birth_day

            db_session.add(query)
            db_session.commit()

            message = f'{query.first_name.capitalize()} {query.family_name.capitalize()} is updated.'

        flash(message)
        return redirect(url_for('index.index'))

    person_id = request.args.get('person_id')
    query = Person.query.options(selectinload(Person.birth)).filter(
        Person.person_id == person_id).first()
    return render_template('data/edit.html', query=query)


@bp.route('/find', methods=('POST',))
@login_required
def find():
    query = Person.query
    message = None

    if request.form.get('nickname'):
        query = Person.query.options(selectinload(Person.birth)).options(selectinload(
            Person.image)).filter(Person.nickname == request.form.get('nickname').lower())
    elif request.form.get('first_name'):
        query = Person.query.options(selectinload(Person.birth)).options(selectinload(
            Person.image)).filter(Person.first_name == request.form.get('first_name').lower())
    elif request.form.get('family_name'):
        query = Person.query.options(selectinload(Person.birth)).options(selectinload(
            Person.image)).filter(Person.family_name == request.form.get('family_name').lower())
    elif request.form.get('first_name') and request.form.get('family_name'):
        query = Person.query.options(selectinload(Person.birth)).options(selectinload(Person.image)).\
            filter(and_(
                Person.first_name == request.form.get(
                    'first_name').lower(),
                Person.family_name == request.form.get('last_name').lower()
            ))
    elif request.form.get('everyone'):
        query = Person.query.options(selectinload(
            Person.birth)).options(selectinload(Person.image))
    else:
        message = 'You have to fill in all the search fields.'

    if query.first() is None:
        message = 'I could not find anyone matching your search terms.'

    if message is None:
        return render_template('data/results.html', query=query)

    flash(message)
    return redirect(url_for('index.index'))


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    if request.method == 'POST':
        person_id = request.args.get('person_id')

        file = request.files.get('file')
        message = 'No image uploaded.'

        # Check if a file is submitted
        if file and file.filename == '':
            message = 'Please select an image file.'
        # Check if jpg or png file
        elif file and not allowed_file(file.filename):
            message = 'Please select a "jpg", "jpeg", or "png" image file.'
        # Secure the filename and save
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename_list = filename.split('.')
            filename_list[0] = person_id
            filename_list[1] = filename_list[1].lower()
            filename = '.'.join(map(str, filename_list))

            # Check if person already has an image
            query = Person.query.options(selectinload(
                Person.image)).filter(Person.person_id).first()
            if query.image:
                # Return to index page
                flash(
                    f'{Person.first_name} {Person.last_name} already has an image.')
                return redirect(url_for(index.index))

            file.save(os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename))

            # Convert image file to thumbnail
            size = (128, 128)

            with open(f"{os.path.join(current_app.config['UPLOAD_FOLDER'], filename)}") as infile:
                infile_str = str(infile.name)

                try:
                    with PIL.Image.open(infile_str) as im:
                        im.thumbnail(size)
                        im.save(infile_str, "JPEG")

                        # Commit thumbnail to images table
                        new_image = Image(
                            image_file=filename, person_id=person_id)
                        db_session.add(new_image)
                        db_session.commit()

                except OSError:
                    print(f'cannot create thumbnail for {infile_str}')

            query = Person.query.filter(
                Person.person_id == person_id).first()

            flash(
                f'Image for {query.first_name.capitalize()} {query.family_name.capitalize()} is saved.')
            return redirect(url_for('index.index'))

        flash(message)
        return render_template('data/upload.index')

    person_id = request.args.get('person_id')
    query = Person.query.filter(Person.person_id == person_id).first()
    return render_template('data/upload.html', query=query)