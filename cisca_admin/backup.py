import csv
import os
from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, send_file, session, url_for
)

from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import Birth, Country, Image, IstdNumber, ChName, Passport, Person, RadNumber, User


bp = Blueprint('backup', __name__, url_prefix='/backup')


@ bp.route('/download', methods=('GET', 'POST'))
@ login_required
def download():
    if request.method == 'POST':
        # Delete existing csv file
        if os.path.exists(os.path.join(
            current_app.config['DOWNLOAD_FOLDER'], 'results.csv')
        ):
            os.remove(os.path.join(
                current_app.config['DOWNLOAD_FOLDER'], 'results.csv'))
        else:
            print('No csv file exists.')

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

        path = f'{current_app.config["DOWNLOAD_FOLDER"]}/results.csv'

        with open(path, 'w') as r:
            writer = csv.writer(r)

            writer.writerow(
                ['nickname', 'firstname', 'middlename', 'familyname', 'CHfamily', 'CHfirst', 'birthyear', 'birthmonth', 'birthday', 'nationality', 'passport', 'rad_number', 'istd_number'])

            for row in query:
                birth_year = None if not row.birth else row.birth.birth_year
                birth_month = None if not row.birth else row.birth.birth_month
                birth_day = None if not row.birth else row.birth.birth_day

                chinese_family = None
                chinese_first = None
                if row.ch_name:
                    chinese_family = None if not row.ch_name.ch_family else row.ch_name.ch_family
                    chinese_first = None if not row.ch_name.ch_first else row.ch_name.ch_first

                if row.countries:
                    for country in row.countries:
                        nationality = country.country_name
                else:
                    nationality = None

                passport = None if not row.passport else row.passport.passport_no
                rad_number = None if not row.rad_number else row.rad_number.rad_pin
                istd_number = None if not row.istd_number else row.istd_number.istd_pin

                writer.writerow(
                    [row.nickname, row.first_name, row.middle_name, row.family_name, chinese_family, chinese_first, birth_year, birth_month, birth_day, nationality, passport, rad_number, istd_number])

        return send_file(path, as_attachment=True)

    # Delete existing csv file
    if os.path.exists(os.path.join(
        current_app.config['DOWNLOAD_FOLDER'], 'results.csv')
    ):
        os.remove(os.path.join(
            current_app.config['DOWNLOAD_FOLDER'], 'results.csv'))
    else:
        print('No csv file exists.')

    return render_template('backup/backup.html')
