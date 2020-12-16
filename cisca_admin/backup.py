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
                ['nickname', 'firstname', 'familyname', 'chinese_names', 'birth', 'nationality', 'passport', 'rad_number', 'istd_number'])

            for row in query:
                writer.writerow(
                    [row.nickname, row.first_name, row.family_name, row.ch_name, row.birth, row.countries, row.passport, row.rad_number, row.istd_number])

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
