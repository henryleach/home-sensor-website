import sqlite3
import click
from flask import current_app, g

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def get_db():
    """ If it doesn't exist create the DB connection
    object, or return an existing one"""

    if 'db' not in g:
        db_path = current_app.config["DATABASE"]
        # print(f"db_path = {db_path}")
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
        
def init_db():
    db = get_db()

    # Create the indexes at start for quicker queries
    with current_app.open_resource('create-indexes.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('create-indexes')
def create_indexes_command():
    """ Create additional indexes on the timestamp
    columns that are queried heavily. Should improve
    query speed.
    """
    init_db()
    click.echo('Added indexes')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(create_indexes_command)
