from sqlalchemy import Column, Integer, String
from cisca_admin.db import db_session, Base


class User(Base):
    query = db_session.query_property()

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String, unique=True)

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.username)
