import re

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Birth, Image, IstdNumber, ChName, Passport, Person, RadNumber, User


bp = Blueprint('edit', __name__, url_prefix='/edit')


@bp.route('/id/<int:person_id>', methods=('GET', 'POST'))
@login_required
def id(person_id):
    if request.method == 'POST':
        # Get form data
        nickname = None if not request.form.get(
            'nickname') else request.form.get('nickname').lower()
        first_name = request.form.get('first_name').lower()
        middle_name = None if not request.form.get(
            'middle_name') else request.form.get('middle_name').lower()
        family_name = request.form.get('family_name').lower()

        ch_first = None if not request.form.get(
            'ch_first') else request.form.get('ch_first').lower()
        ch_family = None if not request.form.get(
            'ch_family') else request.form.get('ch_family').lower()

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

        # Check input on required fields
        if not first_name:
            message = 'First name is required.'
        if not family_name:
            message = 'Family name is required.'

        # Validate birth input
        if birth_year or birth_month or birth_day:
            if birth_year and not re.search("^\d{4}$", birth_year):
                message = 'Please enter the year of birth with four digits, as in "1971".'
            if birth_month and not re.search("^\d{2}$", birth_month):
                message = 'Please enter the month of birth with two digits, as in "12".'
            if birth_day and not re.search("^\d{2}$", birth_day):
                message = 'Please enter the day of birth with two digits, as in "09".'

            if not birth_year or not birth_month or not birth_day:
                message = 'I need all fields completed for date of birth: Year, month, and day.'

        # Input is OK, get existing db values
        if message is None:
            query = Person.query.\
                options(selectinload(Person.birth)).\
                options(selectinload(Person.ch_name)).\
                options(selectinload(Person.passport)).\
                options(selectinload(Person.rad_number)).\
                options(selectinload(Person.istd_number)).\
                filter(Person.person_id == person_id).first()

            # Add English name input
            if nickname != query.nickname:
                query.nickname = nickname
            if first_name != query.first_name:
                query.first_name = first_name
            if middle_name != query.middle_name:
                query.middle_name = middle_name
            if family_name != query.family_name:
                query.family_name = family_name

            # Add Chinese name input
            if query.ch_name and ch_first != query.ch_name.ch_first:
                query.ch_name.ch_first = ch_first
            elif not query.ch_name and ch_first:
                query.ch_name = ChName(ch_first=ch_first)

            if query.ch_name and ch_family != query.ch_name.ch_family:
                query.ch_name.ch_family = ch_family
            elif not query.ch_name and ch_family:
                query.ch_name = ChName(ch_family=ch_family)

            # Delete Chinese name entry if all fields empty
            if query.ch_name and (not ch_first and not ch_family):
                db_session.delete(query.ch_name)

            # Compare and add a complete birthdate input
            if birth_year and birth_month and birth_day:
                query.birth = Birth(
                    birth_year=birth_year,
                    birth_month=birth_month,
                    birth_day=birth_day
                )
            # Delete birth if all birth fields empty
            if query.birth and (not birth_year and not birth_month and not birth_day):
                db_session.delete(query.birth)

            # Add passport input
            if query.passport and passport_no != query.passport.passport_no:
                query.passport.passport_no = passport_no
            elif not query.passport and passport_no:
                query.passport = Passport(passport_no=passport_no)

            # Delete passport entry if field empty
            if query.passport and not passport_no:
                db_session.delete(query.passport)

            # Add RAD number
            if query.rad_number and rad_pin != query.rad_number.rad_pin:
                query.rad_number.rad_pin = rad_pin
            elif not query.rad_number and rad_pin:
                query.rad_number = RadNumber(rad_pin=rad_pin)

            # Delete RAD entry if field empty
            if query.rad_number and not rad_pin:
                db_session.delete(query.rad_number)

            # Add ISTD number
            if query.istd_number and istd_pin != query.istd_number.istd_pin:
                query.istd_number.istd_pin = istd_pin
            elif not query.istd_number and istd_pin:
                query.istd_number = IstdNumber(istd_pin=istd_pin)

            # Delete ISTD entry if field empty
            if query.istd_number and not istd_pin:
                db_session.delete(query.istd_number)

            # Write to db
            db_session.add(query)
            db_session.commit()

            flash(
                f'{query.first_name.capitalize()} {query.family_name.capitalize()} is updated. Please check the details below.')
            return redirect(url_for('person.id', person_id=person_id))

        flash(message)

    query = Person.query.\
        options(selectinload(Person.birth)).\
        options(selectinload(Person.image)).\
        options(selectinload(Person.ch_name)).\
        options(selectinload(Person.passport)).\
        options(selectinload(Person.rad_number)).\
        options(selectinload(Person.istd_number)).\
        filter(Person.person_id == person_id).first()

    return render_template('people/edit.html', person=query)
