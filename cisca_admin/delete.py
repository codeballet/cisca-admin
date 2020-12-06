import os

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, session, url_for
)

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Person

bp = Blueprint('delete', __name__, url_prefix='/delete')


@bp.route('/id/<int:person_id>', methods=('GET', 'POST'))
@login_required
def id(person_id):
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

    return render_template('people/delete.html', person=query)
