import re

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Birth, Country, Image, IstdNumber, ChName, Passport, Person, RadNumber, User

bp = Blueprint('create', __name__, url_prefix='/create')


@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new():
    if request.method == 'POST':
        if request.form.get('nickname'):
            nickname = request.form.get('nickname').lower()
        else:
            nickname = None

        if request.form.get('first_name'):
            first_name = request.form.get('first_name').lower()
        else:
            first_name = None

        if request.form.get('middle_name'):
            middle_name = request.form.get('middle_name').lower()
        else:
            middle_name = None

        if request.form.get('family_name'):
            family_name = request.form.get('family_name').lower()
        else:
            family_name = None

        ch_first = request.form.get(
            'ch_first') if request.form.get('ch_first') else None
        ch_family = request.form.get(
            'ch_family') if request.form.get('ch_family') else None

        country = request.form.get('country')

        birth_year = request.form.get(
            'birth_year') if request.form.get('birth_year') else None
        birth_month = request.form.get(
            'birth_month') if request.form.get('birth_month') else None
        birth_day = request.form.get(
            'birth_day') if request.form.get('birth_day') else None

        passport_no = request.form.get(
            'passport_no') if request.form.get('passport_no') else None
        rad_pin = request.form.get(
            'rad_pin') if request.form.get('rad_pin') else None
        istd_pin = request.form.get(
            'istd_pin') if request.form.get('istd_pin') else None

        message = None

        # Check for required fields
        if not first_name:
            message = 'First name is required.'
        if not family_name:
            message = 'Family name is required.'

        # Validate birth input
        if birth_year and not re.search("^\d{4}$", birth_year):
            message = 'Please enter the year of birth with four digits, as in "1971".'
        if birth_month and not re.search("^\d{2}$", birth_month):
            message = 'Please enter the month of birth with two digits, as in "12".'
        if birth_day and not re.search("^\d{2}$", birth_day):
            message = 'Please enter the day of birth with two digits, as in "09".'

        # Check if names already exist in db
        query = Person.query.options(selectinload(Person.birth)).filter(and_(
            Person.first_name == first_name,
            Person.family_name == family_name)).first()

        if query is not None:
            birth = None if not query.birth else 1
            flash(
                f'Do note that I have another {query.first_name.capitalize()} {query.family_name.capitalize()}{". " if not birth else ", born " + query.birth.birth_year + "-" + query.birth.birth_month + "-" + query.birth.birth_day + ". "} Please delete any double entries.')

        # Everything is OK
        if message is None:
            # Add new person to database
            new_person = Person(first_name=first_name, middle_name=middle_name,
                                family_name=family_name, nickname=nickname)

            if ch_first or ch_family:
                new_person.ch_name = ChName(
                    ch_first=ch_first, ch_family=ch_family)

            if country:
                new_country = Country.query.filter(
                    Country.country_name == country).first()
                new_person.countries.append(new_country)

            if birth_year and birth_month and birth_day:
                new_person.birth = Birth(
                    birth_year=birth_year, birth_month=birth_month, birth_day=birth_day)

            if passport_no:
                new_person.passport = Passport(passport_no=passport_no)

            if rad_pin:
                new_person.rad_number = RadNumber(rad_pin=rad_pin)

            if istd_pin:
                new_person.istd_number = IstdNumber(istd_pin=istd_pin)

            db_session.add(new_person)
            db_session.commit()

            message = f'{first_name.capitalize()} {family_name.capitalize()} is created.'

        flash(message)

    # Get the list of countries from db
    query = Country.query
    return render_template('people/create.html', countries=query)
