from flask import Blueprint, render_template, request, redirect, url_for, make_response
from flask_login import login_user, login_required, logout_user, current_user
from itupass.models import User, Event, Department, UserLecture
from itupass.forms import UserRegistrationForm, LoginForm
from itupass import SUPPORTED_LANGUAGES
from datetime import datetime

client = Blueprint('client', __name__)


@client.route("/")
def index():
    events = Event.get_next_events(limit=8, populate_categories=True)
    return render_template('index.html', events=events)


@client.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        _next = request.args.get('next')
        return redirect(_next or url_for('.index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.get(email=form.email.data)
        if user and user.check_password(form.password.data):
            login_status = login_user(user)
            if not login_status:
                return render_template('user/login.html', form=form, errors="User Disabled, Contact Support!")
            _next = request.args.get('next')
            if _next and _next == "/":
                _next = None
            return redirect(_next or url_for('dashboard.index'))
        else:
            return render_template('user/login.html', form=form, errors="Wrong Credentials")
    return render_template('user/login.html', form=form)


@client.route("/register/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = UserRegistrationForm(request.form)
    form.department.choices = [(dep.code, dep.__str__()) for dep in Department.filter(limit=100, order="code ASC")]
    is_teacher = request.form.get('is_teacher', None) == 'on'
    if request.method == 'POST' and form.validate():
        user = User(
            email=form.email.data,
            password=form.password.data,
            name=form.name.data,
            department=form.department.data,
            is_teacher=is_teacher
        )
        # @TODO disable if is_teacher is true for manual confirmation.
        # @TODO or use email confirmation and later confirm for teachers.
        user = user.save()
        login_user(user)
        return redirect(url_for('.index'))
    return render_template('user/register.html', form=form)


@client.route("/i18n/change/", methods=["GET", "POST"])
@login_required
def change_lang():
    if request.method == 'GET':
        return redirect(url_for('.index'))
    _next = request.form.get('next')
    new_lang = request.form.get('lang', None)
    if new_lang and new_lang in SUPPORTED_LANGUAGES:
        current_user.locale = new_lang
        current_user.save()
    return redirect(_next or url_for('.index'))


@client.route("/logout/", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))


@client.route("/ics/<pk>")
def ics_file(pk):
    pk = pk.replace('.ics', '')
    now = datetime.utcnow()
    start_time = datetime(year=2017, month=9, day=11)
    user = User.get(pk=pk)
    if not user:
        abort(404)
    registrations = UserLecture.filter(student=user.pk, limit=100)
    events = Event.get_next_events(limit=8, populate_categories=True)
    response = make_response(render_template(
        'template.ics', registrations=registrations, events=events, now=now, start_time=start_time
    ).replace('\n\n\n', '\n').replace('\n\n', '\n').replace('\n', '\r\n'))
    response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachement; filename=itupass-calendar.ics'
    return response
