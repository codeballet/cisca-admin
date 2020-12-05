from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash


from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import User

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    if request.method == 'POST':
        user_id = request.args.get('user_id')

        # Read user from db
        query = User.query.filter(
            User.user_id == user_id).first()

        # Check if user is root user
        if query.priviledge == 11:
            flash("I'm sorry, but you cannot delete that user!")
            return redirect(url_for('admin.users'))

        db_session.delete(query)
        db_session.commit()

        flash(f'User {query.username} was deleted.')
        return redirect(url_for('admin.users'))

    user_id = request.args.get('user_id')
    query = User.query.filter(User.user_id == user_id).first()

    return render_template('admin/delete.html', user=query)


@bp.route('/register', methods=('GET', 'POST'))
@login_required
def register():
    if request.method == 'POST':
        username = request.form.get('reg_username')
        password = request.form.get('reg_password')
        priviledge = request.form.get('reg_priviledge') if not request.form.get(
            'reg_priviledge') == 'Priviledge...' else 0
        message = None

        if not username:
            message = 'Username is required.'

        if not password:
            message = 'Password is required.'

        if password != request.form.get('confirm'):
            message = 'Passwords do not match.'

        query = User.query.filter(User.username == username)
        if query.first() is not None:
            message = f'User {username} is already registered'

        # Everything is OK
        if message is None:
            # Hash password
            hashed_password = generate_password_hash(
                password,
                method='pbkdf2:sha512',
                salt_length=128)

            # Add new user to db
            new_user = User(username=username,
                            password=hashed_password,
                            priviledge=priviledge)
            db_session.add(new_user)
            db_session.commit()

            flash(f'New user {username} was added.')
            return redirect(url_for('admin.users'))

        flash(message)

    return render_template('admin/register.html', levels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])


@bp.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        message = None

        # Ensure old password is provided
        if not old_password:
            message = 'Please provide your existing password.'

        # Read existing user from db and verify password
        query = User.query.filter(
            User.user_id == session.get('user_id')).first()

        if not check_password_hash(query.password, old_password):
            message = 'You entered wrong existing password.'

        # Ensure new password is provided
        if not new_password:
            message = 'Please provide a new password.'

        # Verify spelling of new password
        if new_password != confirm_new_password:
            message = 'Please check the spelling of your new password.'

        # Everything is OK
        if message == None:
            # Hash new password
            hashed_password = generate_password_hash(
                new_password,
                method='pbkdf2:sha512',
                salt_length=128)

            # Update password in db
            query.password = hashed_password
            db_session.add(query)
            db_session.commit()

            # Return to index page
            flash('Your password was updated.')
            return redirect(url_for('index.index'))

        flash(message)

    return render_template('admin/settings.html')


@bp.route('/user', methods=('GET', 'POST'))
@login_required
def user():
    if request.method == 'POST':
        # Collect necessary data
        user_id = request.args.get('user_id')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        message = None

        # Read existing user from db
        query = User.query.filter(
            User.user_id == user_id).first()

        # Ensure new password is provided
        if not new_password:
            message = f'Please provide a new password for user.'

        # Verify spelling of new password
        if new_password != confirm_new_password:
            message = f'Please check the spelling of your new password for user.'

        # Everything is OK
        if message == None:
            # Hash new password
            hashed_password = generate_password_hash(
                new_password,
                method='pbkdf2:sha512',
                salt_length=128)

            # Update password in db
            query.password = hashed_password
            db_session.add(query)
            db_session.commit()

            # Return to index page
            flash(f'Password for user {query.username} was updated.')
            return redirect(url_for('index.index'))

        flash(message)

    user_id = request.args.get('user_id')
    query = User.query.filter(User.user_id == user_id).first()
    return render_template('admin/user.html', user=query)


@bp.route('/users', methods=('GET', 'POST'))
@login_required
def users():
    if request.method == 'POST':
        return 'TODO'

    query = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=query)
