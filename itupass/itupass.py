from flask import Flask, g, session

app = Flask('itupass')


def get_db():
    """Open new database connection if there is none."""
    pass


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    pass


@app.before_request
def before_request():
    """Set current user if exists in the session."""
    g.user = None
    if 'user_id' in session:
        g.user = None  # Set to the user object


def init_db():
    """Initializes the database."""
    pass
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initialize database tables and initial values."""
    init_db()
    print('Initialized the database.')
