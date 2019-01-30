import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    # while the app is open, get_db should return the same connection
    with app.app_context():
        db = get_db()
        assert db is get_db()

    # db should be closed if the app context is exited
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e)

# confirm the init_db command can be called
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    # replaces the init_db command with the fake_init_db
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called