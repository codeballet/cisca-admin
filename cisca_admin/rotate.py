import os
import PIL


from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, session, url_for
)

from sqlalchemy.orm import selectinload

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Image, Person


bp = Blueprint('rotate', __name__, url_prefix='/rotate')


@ bp.route('/id/<int:person_id>', methods=('GET', 'POST'))
@ login_required
def id(person_id):
    if request.method == 'POST':
        # Get info about image
        person = Person.query.\
            options(selectinload(Person.image)).\
            filter(Person.person_id == person_id).first()

        # check if image exists
        if os.path.exists(os.path.join(
            current_app.config['UPLOAD_FOLDER'], person.image.image_file)
        ):
            with open(f"{os.path.join(current_app.config['UPLOAD_FOLDER'], person.image.image_file)}") as infile:
                # Extract the filename from the object
                infile_str = str(infile.name)
                print(f'infile_str: {infile_str}')

                # rotate clockwise
                if request.form.get('cw'):
                    try:
                        with PIL.Image.open(infile_str) as im:
                            outfile = im.rotate(-90)
                            outfile.save(infile_str)
                    except OSError:
                        print("Cannot rotate image", infile)

                    return redirect(url_for('rotate.id', person_id=person_id))

                elif request.form.get('ccw'):
                    try:
                        with PIL.Image.open(infile_str) as im:
                            outfile = im.rotate(90)
                            outfile.save(infile_str)
                    except OSError:
                        print("Cannot rotate image", infile)

                    return redirect(url_for('rotate.id', person_id=person_id))

                elif request.form.get('save'):
                    return redirect(url_for('person.id', person_id=person_id))
                
        else:
            flash(
                f'The file {person.image.image_file} for {person.first_name.capitalize()} {person.family_name.capitalize()} does not exist.')

        return redirect(url_for('person.id', person_id=person_id))

    query = Person.query.options(selectinload(Person.image)).filter(
        Person.person_id == person_id).first()
    return render_template('people/rotate.html', person=query)