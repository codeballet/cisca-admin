from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)

from cisca_admin.auth import login_required


bp = Blueprint('index', __name__)


SEARCH_CRITERIA = ['Nickname', 'First name', 'Family name',
                   'First and family name']


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'POST':
        criteria = request.form.get('criteria')

        if criteria == 'Choose search term...':
            flash('Please choose a search term')
            return render_template('index/index.html', search_criteria=SEARCH_CRITERIA)

        return render_template('people/find.html', criteria=criteria, search_criteria=SEARCH_CRITERIA)

    return render_template('index/index.html', search_criteria=SEARCH_CRITERIA)
