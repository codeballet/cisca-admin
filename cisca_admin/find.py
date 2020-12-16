from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from cisca_admin.auth import login_required


bp = Blueprint('find', __name__, url_prefix='/find')


@ bp.route('/terms', methods=('GET', 'POST'))
@ login_required
def terms():
    if request.method == 'POST':
        message = None

        # Check content of the form fields
        if request.form.get('first_name') and request.form.get('family_name'):
            return redirect(url_for('results.table',
                                    first_name=request.form.get(
                                        'first_name').lower(),
                                    family_name=request.form.get('family_name').lower()))
        elif request.form.get('nickname'):
            return redirect(url_for('results.table', nickname=request.form.get('nickname').lower()))
        elif request.form.get('first_name'):
            return redirect(url_for('results.table', first_name=request.form.get('first_name').lower()))
        elif request.form.get('family_name'):
            return redirect(url_for('results.table', family_name=request.form.get('family_name').lower()))
        elif request.form.get('everyone'):
            return redirect(url_for('results.table', everyone=request.form.get('everyone')))

        flash('I could not find anyone.')
        return redirect(url_for('index.index'))

    return redirect(url_for('index.index'))
