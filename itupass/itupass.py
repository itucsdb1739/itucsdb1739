from flask import Flask, g, request
from flask_babel import Babel
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_gravatar import Gravatar
import psycopg2
import os
import json
from raven.contrib.flask import Sentry

from itupass import models


__all__ = ['get_db', 'init_db', 'close_database']


def vcap_to_uri():
    vcap_services = os.environ.get("VCAP_SERVICES")
    if vcap_services:
        parsed = json.loads(vcap_services)
        return parsed["elephantsql"][0]["credentials"]["uri"]
    return None

DEFAULT_BLUEPRINTS = (
    # Add blueprints here
)

# Login Manager
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return models.User.get(user_id)


class Config(object):
    DEBUG = True
    TESTING = True
    DATABASE_URI = os.environ.get("DATABASE_URI")
    SECRET_KEY = os.environ.get("SECRET_KEY", "Not#So@Secret")
    SESSION_COOKIE_NAME = "Ssession"
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['username', 'email']
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "Europe/Istanbul"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DATABASE_URI = vcap_to_uri()
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"
    PERMANENT_SESSION_LIFETIME = 2678400  # in seconds


class TravisConfig(Config):
    DEBUG = False
    TESTING = False

def create_app():
    app = Flask('itupass')
    if os.environ.get("TravisCI", None):
        # It is Travis-CI test build
        app.config.from_object(TravisConfig)
    elif os.environ.get("VCAP_SERVICES", None):
        # IBM Bluemix
        app.config.from_object(ProductionConfig)
    else:
        # Local or unknown environment
        app.config.from_object(Config)
    babel = Babel(app)
    # Enable Sentry in production
    if 'SENTRY_DSN' in app.config:
        sentry = Sentry(app, dsn=app.config['SENTRY_DSN'])

    login_manager.init_app(app)
    # login_manager.login_view = "frontend.login" @TODO
    CSRFProtect(app)
    app.config['gravatar'] = Gravatar(
        app, size=160, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=True, base_url=None
    )
    # Set views
    for view, url_prefix in DEFAULT_BLUEPRINTS:
        app.register_blueprint(view, url_prefix=url_prefix)

    return app, babel


app, babel = create_app()


def _connect_db(app):
    return models.Database(psycopg2.connect(app.config['DATABASE_URI']))


def get_db(app):
    """Open new database connection if there is none."""
    if not hasattr(g, 'database'):
        g.database = _connect_db(app)
    return g.database


@app.teardown_appcontext
def close_database(exception=None):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'database'):
        g.database.close()
        del g.database


def init_db(app):
    """Initializes the database."""
    db = get_db(app)
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor.execute(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initialize database tables and initial values."""
    from itupass.models import User
    app, _ = create_app()
    init_db(app)
    user = User.get(username='admin')
    user.set_password('admin')
    user.save()
    print('Initialized the database.')


@babel.localeselector
def get_locale():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    return request.accept_languages.best_match(['en', 'tr', 'ru'])
