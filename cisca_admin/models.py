from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from cisca_admin.db import db_session, Base


class Birth(Base):
    query = db_session.query_property()

    __tablename__ = 'births'
    person_id = Column(Integer, ForeignKey(
        'people.person_id'), primary_key=True)
    birth_year = Column(String(4), nullable=False)
    birth_month = Column(String(2), nullable=False)
    birth_day = Column(String(2), nullable=False)
    person = relationship("Person", back_populates="birth")

    def __init__(self, birth_year=None, birth_month=None, birth_day=None):
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.birth_day = birth_month

    def __repr__(self):
        return f'<Birth {self.birth_year}-{self.birth_month}-{self.birth_day}>'


class Person(Base):
    query = db_session.query_property()

    __tablename__ = 'people'
    person_id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    family_name = Column(String(50), nullable=False)
    nickname = Column(String(50))
    birth = relationship("Birth", uselist=False,
                         back_populates="person", cascade="all, delete, delete-orphan")

    def __init__(self, first_name=None, middle_name=None, family_name=None, nickname=None):
        self.first_name = first_name
        self.middle_name = middle_name
        self.family_name = family_name
        self.nickname = nickname

    def __repr__(self):
        return f'<Person {self.first_name}, {self.family_name}>'


class User(Base):
    query = db_session.query_property()

    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String, unique=True, nullable=False)

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User {self.username}>'
