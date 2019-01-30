import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data

# confirm that create, update, and delete require user to be logged in
# should get redirected to the login page
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data

# post id's that don't exist return a 404
@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

# create a post
def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    # post the form with title=created, no body
    client.post('/create', data={'title': 'created', 'body': ''})

    # the db post table should have 2 posts now
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2

# update a post
def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    # change the title of the post to 'update', no body
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    # post table in db should have 1 with a matching title now
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


# try to post updates without a title
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data

# delete should return to the index page
def test_delete(client, auth, app):
    auth.login()
    # delete post with id=1
    response = client.post('/1/delete')
    # we get redirected
    assert response.headers['Location'] == 'http://localhost/'

    # confirm post removal from database
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None