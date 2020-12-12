import functools
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from cisca_admin.db import db_session
from cisca_admin.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter(User.user_id == user_id).first()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        message = None

        user = User.query.filter(User.username == username).first()

        if user is None:
            message = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            message = 'Incorrect password.'

        elif message is None:
            session.clear()
            session['user_id'] = user.user_id
            session['privilege'] = user.privilege

            return redirect(url_for('index.index'))

        flash(message)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index.index'))
