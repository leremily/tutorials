import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    # connect to the database if not connected, then return the connection
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    # return the first db in g, close it
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # use the schema file to initialize the database
    # current_app.open_resource -> context manager like open()
    with current_app.open_resource('schema.sql') as db_schema:
        db.executescript(db_schema.read().decode('utf8'))

@click.command('init-db') # makes this a command line command
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db) # runs after a responding to a request
    app.cli.add_command(init_db_command) # adds the init-db to the command line for flask "flask init-db"