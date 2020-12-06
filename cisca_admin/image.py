import os

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, session, url_for
)

from sqlalchemy.orm import selectinload

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Image, Person


bp = Blueprint('image', __name__, url_prefix='/image')


@ bp.route('/id/<int:person_id>', methods=('GET', 'POST'))
@ login_required
def id(person_id):
    if request.method == 'POST':
        # image = Image.query.filter(Image.person_id == person_id).first()
        person = Person.query.\
            options(selectinload(Person.image)).\
            filter(Person.person_id == person_id).first()

        # Delete image file
        if os.path.exists(os.path.join(
            current_app.config['UPLOAD_FOLDER'], person.image.image_file)
        ):
            os.remove(os.path.join(
                current_app.config['UPLOAD_FOLDER'], person.image.image_file))
        else:
            print(
                f'The file {person.image.image_file} for {person.first_name.capitalize()} {person.family_name.capitalize()} does not exist.')

        db_session.delete(person.image)
        db_session.commit()

        if request.form.get('delete'):
            flash(
                f'Image for {person.first_name.capitalize()} {person.family_name.capitalize()} was deleted.')
            return redirect(url_for('person.id', person_id=person_id))

        if request.form.get('change'):
            flash(
                f'Please choose a new image for {person.first_name.capitalize()} {person.family_name.capitalize()}.')
            return redirect(url_for('index.upload', person_id=person_id))

    query = Person.query.options(selectinload(Person.image)).filter(
        Person.person_id == person_id).first()
    return render_template('people/image.html', person=query)
