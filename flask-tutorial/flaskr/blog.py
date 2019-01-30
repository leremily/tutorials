from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

# main page for a blog, lists posts in reverse chronological order
@bp.route('/')
def index():
    db = get_db()
    # get all post entries from the posts table and join them with the author from the user table
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


# create a new blog post, requires the user to be logged in
@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        # input validation
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            # send them back to the index after successful post creation
            return redirect(url_for('blog.index'))
    # if the form was blank (GET) or input couldn't be validated, just stay on the create page
    return render_template('blog/create.html')

# get a post by the id, optionally check that the author of the post matches who is logged in
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    # confirms post author and logged in user id's match
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

# page to update a post, requires login and the post id
# post id signified by <int:id> in the request, flask automatically grabs it
# and passes it to the id argument of update
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        # input validation
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            # rewrite the database entry for the post with the new content
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            # return to home after success
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

# handle a delete post request, then return to home
# example of a request that has no associated template/view
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
