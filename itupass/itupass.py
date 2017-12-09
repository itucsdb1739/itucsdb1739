from flask import Flask, g, request
from flask_babel import Babel
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_gravatar import Gravatar
import psycopg2
import os
from dotenv import load_dotenv, find_dotenv
import json
from raven.contrib.flask import Sentry

from itupass import models
from itupass import views
from itupass import SUPPORTED_LANGUAGES


__all__ = ['get_db', 'init_db', 'close_database']

load_dotenv(find_dotenv(), override=True)

DEFAULT_PASSWORDS = json.load(open('data/users.json'))
# @TODO Source: http://www.sis.itu.edu.tr/tr/sistem/fak_bol_kodlari.html
DEFAULT_DEPARTMENTS = json.load(open('data/departments.json'))


def vcap_to_uri():
    vcap_services = os.environ.get("VCAP_SERVICES")
    if vcap_services:
        parsed = json.loads(vcap_services)
        return parsed["elephantsql"][0]["credentials"]["uri"]
    return None


DEFAULT_BLUEPRINTS = (
    # Add blueprints here
    (views.client, ""),
    (views.admin, "/admin"),
)


class Config(object):
    DEBUG = True
    TESTING = True
    DATABASE_URI = os.environ.get("DATABASE_URI")
    SECRET_KEY = os.environ.get("SECRET_KEY", "Not#So@Secret")
    WTF_CSRF_SECRET_KEY = os.environ.get("SECRET_KEY", "Not#So@Secret")
    SESSION_COOKIE_NAME = "Ssession"
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email']
    LANGUAGES = SUPPORTED_LANGUAGES.keys()
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
    from itupass.models import User, Department
    _app = create_app()
    init_db(_app)
    for code in DEFAULT_DEPARTMENTS:
        Department(code=code, name=DEFAULT_DEPARTMENTS[code]).save()
    for email in DEFAULT_PASSWORDS:
        with User.get(email=email) as user:
            user.department = "BLGE"
            user.set_password(DEFAULT_PASSWORDS[email])
    print("Initialized the database.")


@app.cli.command('parsedata')
def parsedata_command():
    """Parse data from external sources."""
    from itupass.utils import parse_academic_calendar
    parse_academic_calendar()
    print("Data Imported.")


@app.cli.command('parse-lectures')
def parse_lectures_command():
    """Parse lectures for current departments."""
    from itupass.utils import parse_lectures_data
    parse_lectures_data()
    print("Lectures imported.")


@babel.localeselector
def get_locale():
    if current_user.is_authenticated:
        return current_user.locale
    return request.accept_languages.best_match(SUPPORTED_LANGUAGES.keys())


# Template contexts
@app.context_processor
def utility_processor():
    def currentlocale():
        return get_locale()

    def all_locales():
        return SUPPORTED_LANGUAGES.keys()

    return dict(currentlocale=currentlocale, all_locales=all_locales)
