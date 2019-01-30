import pytest
from flask import g, session
from flaskr.db import get_db


# register a user, with username='a' and password='a'
def test_register(client, app):
    # make sure we can get the register page
    assert client.get('/auth/register').status_code == 200
    # fill out a post request
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    # the login view has a header of 'Location' -> indicates success
    assert 'http://localhost/auth/login' == response.headers['Location']

    # make sure the new user got put into the database
    with app.app_context():
        assert get_db().execute(
            "select * from user where username = 'a'",
        ).fetchone() is not None

# test that input validation is working (negative cases)
# no username/password, only username, already existing user
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data