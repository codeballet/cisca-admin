from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy.orm import selectinload

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Birth, Person, User

bp = Blueprint('index', __name__)


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        message = None

        if not first_name:
            flash('Who should I find for you?')
            return redirect(url_for('index.index'))

        query = Person.query.filter(Person.first_name == first_name)

        if query.first() is None:
            message = 'I could not find that person.'

        if message is None:
            return render_template('data/results.html', query=query)

        flash(message)

    return render_template('data/index.html')


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        first_name = request.form.get('first_name').lower()
        middle_name = request.form.get('middle_name').lower()
        family_name = request.form.get('family_name').lower()
        nickname = request.form.get('nickname').lower()
        birth_year = request.form.get('birth_year')
        birth_month = request.form.get('birth_month')
        birth_day = request.form.get('birth_day')
        message = None

        if not first_name:
            message = 'First name is required.'

        if not family_name:
            message = 'Family name is required.'

        query = Person.query.filter(
            Person.first_name == first_name, Person.family_name == family_name)

        if query.first() is not None:
            print(f'All responses: {query.all()}')
            message = f'I already have a person named {first_name.capitalize()}. Are you sure you want to create another one?'

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

        first_name = request.form.get('first_name').lower()
        middle_name = request.form.get('middle_name').lower()
        family_name = request.form.get('family_name').lower()
        nickname = request.form.get('nickname').lower()
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
            if query.nickname != nickname:
                flash(
                    f'Nickname {query.nickname.capitalize()} changed to {nickname.capitalize()}.')
                query.nickname = nickname
            if int(query.birth.birth_year) != int(birth_year):
                flash(
                    f'Birth year {query.birth.birth_year} changed to {birth_year}.')
                query.birth.birth_year = birth_year
            if int(query.birth.birth_month) != int(birth_month):
                flash(
                    f'Birth month {query.birth.birth_month} changed to {birth_month}.')
                query.birth.birth_month = birth_month
            if int(query.birth.birth_day) != int(birth_day):
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
        Person.person_id == person_id).one()
    return render_template('data/edit.html', query=query)
