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
        print(f"db_path = {db_path}")
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
        
def init_db():
    db = get_db()

    # TODO: Is this needed?
    with current_app.open_resource('view_schemas.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables.
    TODO: REMOVE"""

    init_db()
    click.echo('Added views to DB.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
