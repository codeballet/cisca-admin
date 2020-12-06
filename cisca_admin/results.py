from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Birth, Image, IstdNumber, ChName, Passport, Person, RadNumber, User

bp = Blueprint('results', __name__, url_prefix='/results')


@ bp.route('/list', methods=('GET',))
@ login_required
def list():
    message = None
    print(f"url argument: {request.args.get('first_name')}")

    if request.args.get('nickname'):
        query = Person.query.\
            order_by(Person.family_name.asc()).\
            options(selectinload(Person.birth)).\
            options(selectinload(Person.image)).\
            options(selectinload(Person.ch_name)).\
            options(selectinload(Person.passport)).\
            options(selectinload(Person.rad_number)).\
            options(selectinload(Person.istd_number)).\
            filter(Person.nickname == request.args.get('nickname'))
    elif request.args.get('first_name'):
        name = request.args.get('first_name')
        query = Person.query.\
            order_by(Person.family_name.asc()).\
            options(selectinload(Person.birth)).\
            options(selectinload(Person.image)).\
            options(selectinload(Person.ch_name)).\
            options(selectinload(Person.passport)).\
            options(selectinload(Person.rad_number)).\
            options(selectinload(Person.istd_number)).\
            filter(Person.first_name == name)
    elif request.args.get('family_name'):
        query = Person.query.\
            order_by(Person.first_name.asc()).\
            options(selectinload(Person.birth)).\
            options(selectinload(Person.image)).\
            options(selectinload(Person.ch_name)).\
            options(selectinload(Person.passport)).\
            options(selectinload(Person.rad_number)).\
            options(selectinload(Person.istd_number)).\
            filter(Person.family_name == request.args.get('family_name'))
    elif request.args.get('first_name') and request.args.get('family_name'):
        query = Person.query.\
            order_by(Person.person_id.asc()).\
            options(selectinload(Person.birth)).\
            options(selectinload(Person.image)).\
            options(selectinload(Person.ch_name)).\
            options(selectinload(Person.passport)).\
            options(selectinload(Person.rad_number)).\
            options(selectinload(Person.istd_number)).\
            filter(and_(
                Person.first_name == request.args.get('first_name').lower(),
                Person.family_name == request.args.get('family_name').lower()
            ))
    elif request.args.get('everyone'):
        query = Person.query.\
            order_by(
                Person.family_name.asc(),
                Person.first_name.asc()
            ).\
            options(selectinload(Person.birth)).\
            options(selectinload(Person.image)).\
            options(selectinload(Person.ch_name)).\
            options(selectinload(Person.passport)).\
            options(selectinload(Person.rad_number)).\
            options(selectinload(Person.istd_number))
    else:
        # No form fields completed
        message = 'Please fill in all the search fields.'

    # Check query for result
    if query.first() is None:
        message = 'I could not find anyone matching your search terms.'

    # Query is successful, redirect
    if message is None:
        return render_template('people/results.html', query=query)

    # No successful query
    flash(message)
    return redirect(url_for('index.index'))
