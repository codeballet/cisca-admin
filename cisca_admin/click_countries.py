import csv
import click
from flask.cli import with_appcontext

from cisca_admin.db import db_session
from cisca_admin.models import Country


@click.command('countries')
@with_appcontext
def countries():
    with open('./cisca_admin/static/countries.csv', 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            country = Country(country_name=row['country'])
            db_session.add(country)
            db_session.commit()
