from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from itupass.models import Department, Lecture, UserLecture, Event

dashboard = Blueprint('dashboard', __name__)


def student_dashboard():
    registrations = UserLecture.filter(student=current_user.pk, limit=100)
    events = Event.get_next_events(limit=8, populate_categories=True)
    data = {'registrations': registrations, 'events': events}
    return render_template('dashboard/student/index.html', **data)

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


@dashboard.route("/lectures/add", methods=["GET", "POST"])
@login_required
def add_lecture():
    if request.method == 'POST':
        try:
            lecture = int(request.form.get('lecture', None))
        except TypeError:
            abort(404)
        except ValueError:
            abort(404)
        registration = UserLecture(student=current_user.pk, lecture=lecture)
        registration.save()
        return redirect('dashboard.index')
    choosen_department = request.args.get('department')
    if not choosen_department:
        departments = Department.filter(limit=100)
        return render_template('dashboard/student/add_lecture.html', departments=departments)
    lectures = Lecture.department_lectures(department=choosen_department, limit=200)
    return render_template('dashboard/student/add_lecture.html', lectures=lectures)
