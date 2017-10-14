from flask import Blueprint, render_template, current_app, flash, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from itupass.models import User

client = Blueprint('client', __name__)

@client.route("/")
def index():
    data = {}
    return render_template('index.html')


@client.route("/login/", methods=["GET", "POST"])
def login():
    pass