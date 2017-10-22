from flask import Flask, g, request
from flask_babel import Babel
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_gravatar import Gravatar
import psycopg2
import os
from dotenv import load_dotenv, find_dotenv
import json
from raven.contrib.flask import Sentry

from itupass import models
from itupass import views


__all__ = ['get_db', 'init_db', 'close_database']

load_dotenv(find_dotenv(), override=True)

SUPPORTED_LANGUAGES = [
    'en', 'tr', 'ru'
]
DEFAULT_PASSWORDS = {
    'admin@tester.com': 'admin', 'teacher@tester.com': 'teacher', 'tonystark@tester.com': 'tester',
    'elonmusk@tester.com': 'tester', 'mjolnir@tester.com': 'godofthunder',
    'bruce@tester.com': 'mrgreen'
}


def vcap_to_uri():
    vcap_services = os.environ.get("VCAP_SERVICES")
    if vcap_services:
        parsed = json.loads(vcap_services)
        return parsed["elephantsql"][0]["credentials"]["uri"]
    return None


DEFAULT_BLUEPRINTS = (
    # Add blueprints here
    (views.client, ""),
)


class Config(object):
    DEBUG = True
    TESTING = True
    DATABASE_URI = os.environ.get("DATABASE_URI")
    SECRET_KEY = os.environ.get("SECRET_KEY", "Not#So@Secret")
    WTF_CSRF_SECRET_KEY = os.environ.get("SECRET_KEY", "Not#So@Secret")
    SESSION_COOKIE_NAME = "Ssession"
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email']
    LANGUAGES = SUPPORTED_LANGUAGES
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
    _app = Flask('itupass')
    if os.environ.get("TravisCI", None):
        # It is Travis-CI test build
        _app.config.from_object(TravisConfig)
    elif os.environ.get("VCAP_SERVICES", None):
        # IBM Bluemix
        _app.config.from_object(ProductionConfig)
    else:
        # Local or unknown environment
        _app.config.from_object(Config)
    _app.config['gravatar'] = Gravatar(
        _app, size=160, rating='g', default='retro', force_default=False,
        force_lower=False, use_ssl=True, base_url=None
    )
    # Set views
    for view, url_prefix in DEFAULT_BLUEPRINTS:
        _app.register_blueprint(view, url_prefix=url_prefix)

    return _app


app = create_app()
babel = Babel(app)
# Enable Sentry
if 'SENTRY_DSN' in app.config:
    sentry = Sentry(app, dsn=app.config['SENTRY_DSN'])
CSRFProtect(app)
# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "client.login"


@login_manager.user_loader
def load_user(user_id):
    return models.User.get(user_id)


def _connect_db(_app):
    return models.Database(psycopg2.connect(_app.config['DATABASE_URI']))


def get_db(_app):
    """Open new database connection if there is none."""
    if not hasattr(g, 'database'):
        g.database = _connect_db(_app)
    return g.database


@app.teardown_appcontext
def close_database(*_, **__):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'database'):
        g.database.close()
        del g.database


def init_db(_app):
    """Initializes the database."""
    db = get_db(_app)
    with _app.open_resource('schema.sql', mode='r') as f:
        db.cursor.execute(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initialize database tables and initial values."""
    from itupass.models import User
    _app = create_app()
    init_db(_app)
    for email in DEFAULT_PASSWORDS:
        with User.get(email=email) as user:
            user.set_password(DEFAULT_PASSWORDS[email])
    print("Initialized the database.")


@app.cli.command('parsedata')
def parsedata_command():
    """Parse data from external sources."""
    from itupass.utils import parse_academic_calendar
    parse_academic_calendar()
    print("Data Imported.")


@babel.localeselector
def get_locale():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    return request.accept_languages.best_match(SUPPORTED_LANGUAGES)


# Template contexts
@app.context_processor
def utility_processor():
    def currentlocale():
        return get_locale()
    return dict(currentlocale=currentlocale)
