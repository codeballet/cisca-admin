import os
import PIL
import re

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)

from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from werkzeug.utils import secure_filename

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Birth, Image, NativeName, Person, User
from cisca_admin.helpers import allowed_file

bp = Blueprint('index', __name__)

SEARCH_CRITERIA = ['Nickname', 'First name', 'Family name',
                   'First and family name']


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'POST':
        criteria = request.form.get('criteria')

        if criteria == 'Choose search term...':
            flash('Please choose a search term')
            return render_template('data/index.html', search_criteria=SEARCH_CRITERIA)

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
        native_first = '' if not request.form.get('native_first') \
            else request.form.get('native_first').lower()
        native_middle = '' if not request.form.get('native_middle') \
            else request.form.get('native_middle').lower()
        native_family = '' if not request.form.get('native_family') \
            else request.form.get('native_family').lower()
        birth_year = request.form.get('birth_year')
        birth_month = request.form.get('birth_month')
        birth_day = request.form.get('birth_day')
        message = None

        if not first_name:
            message = 'First name is required.'
        elif not family_name:
            message = 'Family name is required.'
        elif not re.search("^\d{4}$", birth_year):
            message = 'Please enter the year of birth with four digits, as in "1971".'
        elif not re.search("^\d{2}$", birth_month):
            message = 'Please enter the month of birth with two digits, as in "12".'
        elif not re.search("^\d{2}$", birth_day):
            message = 'Please enter the day of birth with two digits, as in "09".'

        query = Person.query.options(selectinload(Person.birth)).filter(and_(
            Person.first_name == first_name,
            Person.family_name == family_name)).first()

        if query is not None:
            message = f'I already have {query.first_name.capitalize()} {query.family_name.capitalize()}{". " if not query.birth.birth_year else ", born " + query.birth.birth_year + "-" + query.birth.birth_month + "-" + query.birth.birth_day + ". "} Are you sure you want to add another?'

        if message is None:
            new_person = Person(first_name=first_name, middle_name=middle_name,
                                family_name=family_name, nickname=nickname)
            new_person.native_name = NativeName(
                native_first=native_first, native_middle=native_middle, native_family=native_family)
            new_person.birth = Birth(
                birth_year=birth_year, birth_month=birth_month, birth_day=birth_day)
            db_session.add(new_person)
            db_session.commit()

            message = f'{first_name.capitalize()} {family_name.capitalize()} is created.'

        flash(message)

    return render_template('data/create.html')


@bp.route('/delete/<int:person_id>', methods=('GET', 'POST'))
@login_required
def delete(person_id):
    if request.method == 'POST':
        # Read user from db
        query = Person.query.filter(
            Person.person_id == person_id).first()

        print(f'query image from delete: {query.image}')

        # Delete image file
        if query.image:
            if os.path.exists(os.path.join(
                current_app.config['UPLOAD_FOLDER'], query.image.image_file)
            ):
                os.remove(os.path.join(
                    current_app.config['UPLOAD_FOLDER'], query.image.image_file))
            else:
                print(f'The file {query.image.image_file} does not exist.')

        # Delete user
        db_session.delete(query)
        db_session.commit()

        flash(
            f'{query.first_name.capitalize()} {query.family_name.capitalize()} was deleted.')
        return redirect(url_for('index.index'))

    query = Person.query.filter(Person.person_id == person_id).first()

    return render_template('data/delete.html', person=query)


@bp.route('/edit/<int:person_id>', methods=('GET', 'POST'))
@login_required
def edit(person_id):
    if request.method == 'POST':
        # Get form data
        print(f'person_id in edit view: {person_id}')
        nickname = request.form.get('nickname').lower()
        first_name = request.form.get('first_name').lower()
        middle_name = request.form.get('middle_name').lower()
        family_name = request.form.get('family_name').lower()
        birth_year = request.form.get('birth_year')
        birth_month = request.form.get('birth_month')
        birth_day = request.form.get('birth_day')
        message = None

        # Check input on required fields
        if not first_name:
            message = 'First name is required.'
        elif not family_name:
            message = 'Family name is required.'
        elif not re.search("^\d{4}$", birth_year):
            message = 'Please enter the year of birth with four digits, as in "1971".'
        elif not re.search("^\d{2}$", birth_month):
            message = 'Please enter the month of birth with two digits, as in "12".'
        elif not re.search("^\d{2}$", birth_day):
            message = 'Please enter the day of birth with two digits, as in "09".'

        # Everything is OK
        if message is None:
            query = Person.query.options(selectinload(Person.birth)).options(selectinload(Person.image)).filter(
                Person.person_id == person_id).first()

            if query.nickname != nickname:
                flash(f"{query.first_name.capitalize()} {query.family_name.capitalize()}'s nickname {query.nickname.capitalize()} changed to {nickname.capitalize()}.")
                query.nickname = nickname
            if query.first_name != first_name:
                flash(f"{query.first_name.capitalize()} {query.family_name.capitalize()}'s first name {query.first_name.capitalize()} changed to {first_name.capitalize()}.")
                query.first_name = first_name
            if query.middle_name != middle_name:
                flash(f"{query.first_name.capitalize()} {query.family_name.capitalize()}'s middle name {query.middle_name.capitalize()} changed to {middle_name.capitalize()}.")
                query.middle_name = middle_name
            if query.family_name != family_name:
                flash(f"{query.first_name.capitalize()} {query.family_name.capitalize()}'s family name {query.family_name.capitalize()} changed to {family_name.capitalize()}.")
                query.family_name = family_name
            if query.birth.birth_year != birth_year:
                flash(f"{query.first_name.capitalize()} {query.family_name.capitalize()}'s birth year {query.birth.birth_year} changed to {birth_year}.")
                query.birth.birth_year = birth_year
            if query.birth.birth_month != birth_month:
                flash(f"{query.first_name.capitalize()} {query.family_name.capitalize()}'s birth month {query.birth.birth_month} changed to {birth_month}.")
                query.birth.birth_month = birth_month
            if query.birth.birth_day != birth_day:
                flash(f"{query.first_name.capitalize()} {query.family_name.capitalize()}'s birthday {query.birth.birth_day} changed to {birth_day}.")
                query.birth.birth_day = birth_day

            db_session.add(query)
            db_session.commit()

            message = f'{query.first_name.capitalize()} {query.family_name.capitalize()} is updated.'
            return redirect(url_for('index.index'))

        flash(message)

    query = Person.query.options(selectinload(Person.birth)).options(selectinload(Person.image)).filter(
        Person.person_id == person_id).first()
    return render_template('data/edit.html', person=query)


@bp.route('/find', methods=('POST',))
@login_required
def find():
    message = None

    # Check content of the form fields
    if request.form.get('nickname'):
        return redirect(url_for('index.results', nickname=request.form.get('nickname')))
    elif request.form.get('first_name'):
        return redirect(url_for('index.results', first_name=request.form.get('first_name')))
    elif request.form.get('family_name'):
        return redirect(url_for('index.results', family_name=request.form.get('family_name')))
    elif request.form.get('first_name') and request.form.get('family_name'):
        return redirect(url_for('index.results',
                                first_name=request.form.get('first_name'),
                                family_name=request.form.get('family_name')))
    elif request.form.get('everyone'):
        return redirect(url_for('index.results', everyone=request.form.get('everyone')))

    flash('I could not find anyone.')
    return redirect(url_for('index.index'))


@ bp.route('/image/<int:person_id>', methods=('GET', 'POST'))
@ login_required
def image(person_id):
    if request.method == 'POST':
        image = Image.query.filter(Image.person_id == person_id).first()
        person = Person.query.filter(Person.person_id == person_id).first()

        # Delete image file
        if os.path.exists(os.path.join(
            current_app.config['UPLOAD_FOLDER'], image.image_file)
        ):
            os.remove(os.path.join(
                current_app.config['UPLOAD_FOLDER'], image.image_file))
        else:
            print(
                f'The file {image.image_file} for {person.first_name.capitalize()} {person.family_name.capitalize()} does not exist.')

        db_session.delete(image)
        db_session.commit()

        if request.form.get('delete'):
            flash(
                f'Image for {person.first_name.capitalize()} {person.family_name.capitalize()} was deleted.')
            return redirect(url_for('index.index'))

        if request.form.get('change'):
            flash(
                f'Please choose a new image for {person.first_name.capitalize()} {person.family_name.capitalize()}.')
            return redirect(url_for('index.upload', person_id=person_id))

    query = Person.query.options(selectinload(Person.image)).filter(
        Person.person_id == person_id).first()
    return render_template('data/image.html', person=query)


@ bp.route('/results', methods=('GET',))
@ login_required
def results():
    message = None

    if request.args.get('nickname'):
        query = Person.query.options(selectinload(Person.birth)).options(selectinload(Person.image)).options(
            selectinload(Person.native_name)).filter(Person.nickname == request.args.get('nickname').lower())
    elif request.args.get('first_name'):
        query = Person.query.options(selectinload(Person.birth)).options(selectinload(Person.image)).options(
            selectinload(Person.native_name)).filter(Person.first_name == request.args.get('first_name'))
    elif request.args.get('family_name'):
        query = Person.query.options(selectinload(Person.birth)).options(selectinload(Person.image)).options(
            selectinload(Person.native_name)).filter(Person.family_name == request.args.get('family_name').lower())
    elif request.args.get('first_name') and request.args.get('family_name'):
        query = Person.query.\
            options(selectinload(Person.birth)).\
            options(selectinload(Person.image)).\
            options(selectinload(Person.native_name)).\
            filter(and_(
                Person.first_name == request.args.get('first_name').lower(),
                Person.family_name == request.args.get('family_name').lower()
            ))
    elif request.args.get('everyone'):
        query = Person.query.options(selectinload(Person.birth)).options(
            selectinload(Person.image)).options(selectinload(Person.native_name))
    # No form fields completed
    else:
        message = 'You have to fill in all the search fields.'

    # Check query for result
    if query.first() is None:
        message = 'I could not find anyone matching your search terms.'

    # Query is successful, redirect
    if message is None:
        return render_template('data/results.html', query=query)

    # No successful query
    flash(message)
    return redirect(url_for('index.index'))


@ bp.route('/upload/<int:person_id>', methods=('GET', 'POST'))
@ login_required
def upload(person_id):
    if request.method == 'POST':
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
                    f'{query.first_name.capitalize()} {query.family_name.capitalize()} already has an image.')
                return redirect(url_for('index.index'))

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

    query = Person.query.filter(Person.person_id == person_id).first()
    return render_template('data/upload.html', person=query)
