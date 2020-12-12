from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash


from cisca_admin.auth import login_required
from cisca_admin.db import db_session
from cisca_admin.models import User

bp = Blueprint('admin', __name__, url_prefix='/admin')


LEVELS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    if request.method == 'POST':
        user_id = request.args.get('user_id')

        # Read user from db
        query = User.query.filter(
            User.user_id == user_id).first()

        # Check if user is root user
        if query.privilege == 11:
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
        privilege = request.form.get('reg_privilege') if not request.form.get(
            'reg_privilege') == 'Privilege...' else 0
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
                            privilege=privilege)
            db_session.add(new_user)
            db_session.commit()

            flash(f'New user {username} was added.')
            return redirect(url_for('admin.users'))

        flash(message)

    return render_template('admin/register.html', levels=LEVELS)


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


@bp.route('/user/<int:user_id>', methods=('GET', 'POST'))
@login_required
def user(user_id):
    if request.method == 'POST':
        # Collect necessary data
        username = request.form.get('username')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        new_privilege = request.form.get('new_privilege')
        message = None

        # Read existing user from db
        query = User.query.filter(
            User.user_id == user_id).first()

        old_username = query.username
        old_privilege = query.privilege

        # Ensure username is provided
        if not username:
            message = f'Please provide a username.'

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

            # Update username, password, and privilege in db if submitted
            if username and username != old_username:
                query.username = username
                flash(
                    f'Username for {old_username} was updated to {username}.')
            if new_password and new_password == confirm_new_password:
                query.password = hashed_password
                flash(
                    f'Password for {username if username else old_username} updated.')
            if new_privilege != 'Privilege...' and new_privilege != old_privilege:
                query.privilege = new_privilege
                flash(
                    f'Privilege for {username if username else old_username} is updated from {old_privilege} to {new_privilege}.')
            if username or new_password:
                db_session.add(query)
                db_session.commit()

            # Return to index page
            return redirect(url_for('index.index'))

        flash(message)

    query = User.query.filter(User.user_id == user_id).first()
    return render_template('admin/user.html', user=query, levels=LEVELS)


@bp.route('/users', methods=('GET', 'POST'))
@login_required
def users():
    if request.method == 'POST':
        return 'TODO'

    query = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=query)
