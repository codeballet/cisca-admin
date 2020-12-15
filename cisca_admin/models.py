from sqlalchemy import ForeignKey, Column, Integer, String, Table
from sqlalchemy.orm import relationship
from cisca_admin.db import db_session, Base


# association tables
people_countries = Table('people_countries', Base.metadata,
    Column('person_id', ForeignKey('people.person_id'), primary_key=True),
    Column('country_id', ForeignKey('countries.country_id'), primary_key=True)
)


# Model classes
class Birth(Base):
    query = db_session.query_property()

    __tablename__ = 'births'
    birth_id = Column(Integer, primary_key=True)
    person_id = Column(Integer,
                       ForeignKey('people.person_id', ondelete="CASCADE"))
    birth_year = Column(String(4), nullable=False)
    birth_month = Column(String(2), nullable=False)
    birth_day = Column(String(2), nullable=False)

    person = relationship("Person", back_populates="birth")

    def __init__(self, birth_year=None, birth_month=None, birth_day=None):
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.birth_day = birth_day

    def __repr__(self):
        return f'<Birth {self.birth_year}-{self.birth_month}-{self.birth_day}>'


class ChName(Base):
    query = db_session.query_property()

    __tablename__ = "ch_names"
    ch_id = Column(Integer, primary_key=True)
    ch_first = Column(String(50))
    ch_family = Column(String(50))
    person_id = Column(Integer, ForeignKey(
        'people.person_id', ondelete="CASCADE"))

    person = relationship("Person", back_populates="ch_name")

    def __init__(self, ch_first=None, ch_family=None):
        self.ch_first = ch_first
        self.ch_family = ch_family

    def __repr__(self):
        return f'<ChName {self.ch_first}, {self.ch_family}>'


class Country(Base):
    query = db_session.query_property()

    __tablename__ = "countries"
    country_id = Column(Integer, primary_key=True)
    country_name = Column(String, unique=True, nullable=False)

    # many to many
    people = relationship(
        'Person',
        secondary=people_countries,
        back_populates='countries')

    def __init__(self, country_name=None):
        self.country_name = country_name

    def __repr__(self):
        return f'<Country {self.country_name}>'


class Image(Base):
    query = db_session.query_property()

    __tablename__ = 'images'
    image_id = Column(Integer, primary_key=True)
    image_file = Column(String(10), unique=True, nullable=False)
    person_id = Column(
        Integer,
        ForeignKey('people.person_id', ondelete="CASCADE")
    )

    person = relationship("Person", back_populates="image")

    def __init__(self, image_file=None, person_id=None):
        self.image_file = image_file
        self.person_id = person_id

    def __repr__(self):
        return f'<Image {self.image_file}>'


class IstdNumber(Base):
    query = db_session.query_property()

    __tablename__ = 'istd_numbers'
    istd_id = Column(Integer, primary_key=True)
    istd_pin = Column(String(10), unique=True, nullable=False)
    person_id = Column(
        Integer,
        ForeignKey('people.person_id', ondelete="CASCADE")
    )

    person = relationship("Person", back_populates="istd_number")

    def __init__(self, istd_pin=None, person_id=None):
        self.istd_pin = istd_pin
        self.person_id = person_id

    def __repr__(self):
        return f'<IstdNumber {self.istd_pin}, {self.person_id}>'


class Passport(Base):
    query = db_session.query_property()

    __tablename__ = 'passports'
    passport_id = Column(Integer, primary_key=True)
    passport_no = Column(String(30), unique=True, nullable=False)
    person_id = Column(Integer, ForeignKey(
        'people.person_id', ondelete="CASCADE"
    ))

    person = relationship("Person", back_populates="passport")

    def __init__(self, passport_no=None, person_id=None):
        self.passport_no = passport_no
        self.person_id = person_id

    def __repr__(self):
        return f'<Passport {self.passport_no}, {self.person_id}>'


class Person(Base):
    query = db_session.query_property()

    __tablename__ = 'people'
    person_id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    family_name = Column(String(50), nullable=False)
    nickname = Column(String(50))

    # one to one
    birth = relationship(
        "Birth", uselist=False,
        back_populates="person",
        cascade="all, delete, delete-orphan"
    )
    ch_name = relationship(
        "ChName", uselist=False,
        back_populates="person",
        cascade="all, delete, delete-orphan"
    )
    image = relationship(
        "Image", uselist=False,
        back_populates="person",
        cascade="all, delete, delete-orphan"
    )
    istd_number = relationship(
        "IstdNumber", uselist=False,
        back_populates="person",
        cascade="all, delete, delete-orphan"
    )
    passport = relationship(
        "Passport", uselist=False,
        back_populates="person",
        cascade="all, delete, delete-orphan"
    )
    rad_number = relationship(
        "RadNumber", uselist=False,
        back_populates="person",
        cascade="all, delete, delete-orphan"
    )

    # many to many
    countries = relationship(
        'Country',
        secondary=people_countries,
        lazy='subquery',
        back_populates='people'
    )

    def __init__(self, first_name=None, middle_name=None, family_name=None, nickname=None):
        self.first_name = first_name
        self.middle_name = middle_name
        self.family_name = family_name
        self.nickname = nickname

    def __repr__(self):
        return f'<Person {self.first_name}, {self.family_name}>'


class RadNumber(Base):
    query = db_session.query_property()

    __tablename__ = 'rad_numbers'
    rad_id = Column(Integer, primary_key=True)
    rad_pin = Column(String(10), unique=True, nullable=False)
    person_id = Column(Integer, ForeignKey(
        'people.person_id', ondelete="CASCADE"
    ))

    person = relationship("Person", back_populates="rad_number")

    def __init__(self, rad_pin=None, person_id=None):
        self.rad_pin = rad_pin
        self.person_id = person_id

    def __repr__(self):
        return f'<RadNumber {self.rad_pin}, {self.person_id}>'


class User(Base):
    query = db_session.query_property()

    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String, nullable=False)
    privilege = Column(Integer, nullable=False, default=0)

    def __init__(self, username=None, password=None, privilege=None):
        self.username = username
        self.password = password
        self.privilege = privilege

    def __repr__(self):
        return f'<User {self.username}>'
