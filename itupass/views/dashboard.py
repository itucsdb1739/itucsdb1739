from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from itupass.models import Department, Lecture, Event

dashboard = Blueprint('dashboard', __name__)


def student_dashboard():
    return render_template('dashboard/student.html')

def teacher_dashboard():
    return render_template('dashboard/teacher.html')

def staff_dashboard():
    return render_template('dashboard/staff.html')


@dashboard.route("/")
@login_required
def index():
    if current_user.is_staff:
        return staff_dashboard()
    if current_user.is_teacher:
        return teacher_dashboard()
    return student_dashboard()
