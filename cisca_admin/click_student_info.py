import csv
import click
from flask.cli import with_appcontext

from cisca_admin.db import db_session
from cisca_admin.models import Birth, Country, Image, IstdNumber, ChName, Passport, Person, RadNumber


@click.command('student-info')
@with_appcontext
def student_info():
    with open('./cisca_admin/static/student-info.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            person = Person(
                first_name=row['firstname'].lower(),
                middle_name=row['middlename'].lower(),
                family_name=row['familyname'].lower(),
                nickname=row['nickname'].lower()
            )

            country = row['nationality']
            if country:
                new_country = Country.query.filter(
                    Country.country_name == country
                ).first()
                if new_country:
                    person.countries.append(new_country)

            birthday = row['birthday']
            if birthday:
                birth_list = birthday.split('/')
                person.birth = Birth(
                    birth_year=str(birth_list[2]),
                    birth_month=str(birth_list[1]),
                    birth_day=str(birth_list[0])
                )

            db_session.add(person)
            db_session.commit()
