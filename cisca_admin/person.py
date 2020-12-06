from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Birth, Image, IstdNumber, ChName, Passport, Person, RadNumber, User

bp = Blueprint('person', __name__, url_prefix='/person')


@ bp.route('/id/<int:person_id>', methods=('GET',))
@ login_required
def id(person_id):
    query = Person.query.\
        options(selectinload(Person.birth)).\
        options(selectinload(Person.image)).\
        options(selectinload(Person.ch_name)).\
        options(selectinload(Person.passport)).\
        options(selectinload(Person.rad_number)).\
        options(selectinload(Person.istd_number)).\
        filter(Person.person_id == person_id).first()

    return render_template('people/person.html', person=query)
