import os

from flask import Flask

from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Numeric, ForeignKey, select, insert, update, delete, and_
)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'cisca.db')
    )

    if test_config is None:
        # load the instance config if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # insure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Configure SQLAlchemy to use SQLite database
    engine = create_engine(f'sqlite:///{app.config["DATABASE"]}', echo=True)

    # Define tables for SQLAlchemy
    metadata = MetaData()

    people = Table('people', metadata,
        Column('person_id', Integer, primary_key=True),
        Column('first_name', String(50), nullable=False),
        Column('middle_name', String(50)),
        Column('last_name', String(50), nullable=False),
        Column('nickname', String)
    )

    # Create tables for SQLAlchemy
    metadata.create_all(engine)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
