import os

from flask import Flask, render_template
from flask_session import Session

from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

from cisca_admin.db import db_session, init_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SESSION_TYPE='filesystem',
        SESSION_PERMANENT=False,
        TEMPLATES_AUTO_RELOAD=True,
        UPLOAD_FOLDER=os.path.abspath('cisca_admin/static/images')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure responses aren't cached
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    # Configure session to use Session
    Session(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    init_db()

    from . import admin
    app.register_blueprint(admin.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import create
    app.register_blueprint(create.bp)

    from . import delete
    app.register_blueprint(delete.bp)

    from . import edit
    app.register_blueprint(edit.bp)

    from . import find
    app.register_blueprint(find.bp)

    from . import image
    app.register_blueprint(image.bp)

    from . import index
    app.register_blueprint(index.bp)
    app.add_url_rule('/', endpoint='index')

    from . import person
    app.register_blueprint(person.bp)

    from . import results
    app.register_blueprint(results.bp)

    from . import upload
    app.register_blueprint(upload.bp)

    return app

    def errorhandler(e):
        """Handle error"""
        if not isinstance(e, HTTPException):
            e = InternalServerError()
        return render_template('error/error.html', name=e.name, code=e.code)

    # Listen for errors
    for code in default_exceptions:
        app.errorhandler(code)(errorhandler)
