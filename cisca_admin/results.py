from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from flask_paginate import Pagination, get_page_args

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Birth, Country, Image, IstdNumber, ChName, Passport, Person, RadNumber, User

bp = Blueprint('results', __name__, url_prefix='/results')


@ bp.route('/table', methods=('GET',))
@ login_required
def table():
    message = None

    if request.args.get('first_name') and request.args.get('family_name'):
        query = Person.query.\
            order_by(Person.person_id.asc()).\
            options(selectinload(Person.birth)).\
            options(selectinload(Person.image)).\
            options(selectinload(Person.ch_name)).\
            options(selectinload(Person.passport)).\
            options(selectinload(Person.rad_number)).\
            options(selectinload(Person.istd_number)).\
            filter(and_(
                Person.first_name == request.args.get('first_name'),
                Person.family_name == request.args.get('family_name')
            ))
    elif request.args.get('nickname'):
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
            options(selectinload(Person.istd_number)).\
            options(selectinload(Person.countries))
    else:
        # No form fields completed
        message = 'Please fill in all the search fields.'

    # Check query for result
    if query.first() is None:
        message = 'I could not find anyone matching your search terms.'

    # Query is successful, redirect
    if message is None:
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = 10
        offset = (page - 1) * per_page
        query_for_render = query.limit(per_page).offset(offset)

        search = False

        q = request.args.get('q')
        if q:
            search = True

        pagination = Pagination(
            page=page,
            per_page=per_page,
            offset=offset,
            total=query.count(),
            css_framework='bootstrap4',
            search=search
        )

        return render_template('people/results.html', query=query_for_render, pagination=pagination)

    # No successful query
    flash(message)
    return redirect(url_for('index.index'))
