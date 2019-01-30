import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    )

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# blueprint for pages related to registering, logging in, logging out
# and requiring login
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Registration Page
# return the 'register' view when [URL]/auth/register is requested
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # if the form is filled out, request type will be POST
    # validate the input
    # request.form is a dict mapping of the submitted form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # validation: username, password, username does not already exist in db
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        # success!, insert the new username and hashed password into the db
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        # flash allows the template to render an error message, if any
        flash(error)

    # return the filled in template
    return render_template('auth/register.html')

# Login Page
# return the 'login' view with [URL]/login is requested
@bp.route('/login', methods=('GET', 'POST'))
def login():
    # try to sign in if form was filled in, e.g. request type POST
    # otherwise, return the login page
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # validate inputs
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is dict that stores data across multiple requests
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# bp.before_app_request decorator marks a function to run before any request is processed
# this one checks if they're currently logged in, grabs their info from the db if they are
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# clears the user info from the session when they request [URL]/logout
# then returns the home page
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# a decorator to be used elsewhere
# for requiring a user to be logged in before responding to certain requests
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # if user is not logged in, return the login page instead of the requested view
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view