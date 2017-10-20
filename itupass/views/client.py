from flask import Blueprint, render_template, current_app, flash, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from itupass.models import User
from itupass.forms import UserForm, LoginForm

client = Blueprint('client', __name__)

@client.route("/")
def index():
    data = {}
    return render_template('index.html')


@client.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        _next = request.args.get('next')
        return redirect(_next or url_for('.index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.get(username=form.username.data)
        if user and user.check_password(form.password.data):
            login_status = login_user(user)
            if not login_status:
                return render_template('user/login.html', form=form, errors="User Disabled, Contact Support!")
            _next = request.args.get('next')
            return redirect(_next or url_for('.index'))
        else:
            return render_template('user/login.html', form=form, errors="Wrong Credentials")
    return render_template('user/login.html', form=form)

@client.route("/register/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            name=form.name.data,
            is_teacher=form.is_teacher.data
        )
        # @TODO disable if is_teacher is true for manual confirmation.
        # @TODO or use email confirmation and later confirm for teachers.
        user = user.save()
        login_user(user)
        return redirect(url_for('.index'))
    return render_template('user/register.html', form=form)

@client.route("/logout/", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))
