from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_user, login_required, logout_user, current_user
from itupass.models import Paginator, Department, User, Lecture, EventCategory, Event
from itupass.forms import UserAdminForm, LectureForm, EventForm
from itupass.utils import admin_required

admin = Blueprint('admin', __name__)


@admin.route("/")
@login_required
@admin_required
def admin_index():
    current_year = datetime.now().year
    data = {}
    data["active_users_count"] = User.count(deleted=False)
    data["users_count"] = User.count()
    data["lectures_count"] = Lecture.count(year=current_year+1)
    data["departments_count"] = Department.count()
    data["event_cats_count"] = EventCategory.count()
    data["events_count"] = Event.count()
    return render_template("admin/index.html", **data)

@admin.route("/users")
@admin.route("/users/<pk>", methods=["GET", "POST"])
@login_required
@admin_required
def users_admin(pk=None):
    if pk:
        user = User.get(pk=pk)
        if not user:
            abort(404)
        if request.form:
            form = UserAdminForm(request.form)
        else:
            form = UserAdminForm(
                name=user.name,
                email=user.email,
                department=user.department,
                deleted=user.deleted,
                is_teacher=user.is_teacher,
                is_staff=user.is_staff,
                locale=user.locale
            )
        form.department.choices = [(dep.code, dep.__str__()) for dep in Department.filter(limit=100, order="code ASC")]
        if request.method == 'POST' and form.validate():
            user.name = form.name.data
            user.email = form.email.data
            user.department = form.department.data
            user.deleted = form.deleted.data
            user.is_teacher = form.is_teacher.data
            user.is_staff = form.is_staff.data
            user.locale = form.locale.data
            user.save()
            return redirect(url_for('.users_admin'))
        return render_template('admin/users_edit.html', form=form, user=user)
    items_per_page = 12
    data = {"limit": items_per_page}
    try:
        page = int(request.args.get('page'))
    except ValueError:
        page = 1
    except TypeError:
        page = 1
    data["users_count"] = User.count()
    total_pages = int(data["users_count"] / items_per_page + 0.99)
    if page:
        if page > total_pages:
            page = 1
    else:
        page = 1
    offset = (page - 1) * items_per_page
    data["users"] = User.filter(limit=items_per_page, offset=offset)
    data["pagination"] = Paginator(current_page=page, total_pages=total_pages)
    return render_template("admin/users.html", **data)

@admin.route("/users/<pk>/disable", methods=["POST"])
@login_required
@admin_required
def users_disable(pk):
    try:
        user = User.get(pk=int(pk))
    except Exception:
        user = None
    if not user:
        return abort(404)
    user.disable()
    return redirect(url_for('.users_admin'))

@admin.route("/users/<pk>/delete", methods=["POST"])
@login_required
@admin_required
def users_delete(pk):
    try:
        user = User.get(pk=int(pk))
    except Exception:
        user = None
    if not user:
        return abort(404)
    user.delete()
    return redirect(url_for('.users_admin'))

### Lectures
@admin.route("/lectures")
@admin.route("/lectures/<pk>", methods=["GET", "POST"])
@login_required
@admin_required
def lectures_admin(pk=None):
    if pk:
        lecture = Lecture.get(pk=pk)
        if not lecture:
            abort(404)
        if request.form:
            form = LectureForm(request.form)
        else:
            form = LectureForm(
                name=lecture.name,
                crn=lecture.crn,
                code=lecture.code,
                instructor=lecture.instructor,
                year=lecture.year,
            )
        if request.method == 'POST' and form.validate():
            lecture.name = form.name.data
            lecture.crn = form.crn.data
            lecture.code = form.code.data
            lecture.instructor = form.instructor.data
            lecture.year = form.year.data
            lecture.save()
            return redirect(url_for('.lectures_admin'))
        return render_template('admin/lectures_edit.html', form=form, lecture=lecture)
    items_per_page = 12
    data = {"limit": items_per_page}
    try:
        page = int(request.args.get('page'))
    except ValueError:
        page = 1
    except TypeError:
        page = 1
    data["lectures_count"] = Lecture.count()
    total_pages = int(data["lectures_count"] / items_per_page + 0.99)
    if page:
        if page > total_pages:
            page = 1
    else:
        page = 1
    offset = (page - 1) * items_per_page
    data["lectures"] = Lecture.filter(limit=items_per_page, offset=offset)
    data["pagination"] = Paginator(current_page=page, total_pages=total_pages)
    return render_template("admin/lectures.html", **data)

@admin.route("/lectures/<pk>/delete", methods=["POST"])
@login_required
@admin_required
def lectures_delete(pk):
    try:
        lecture = Lecture.get(pk=int(pk))
    except Exception:
        lecture = None
    if not lecture:
        return abort(404)
    lecture.delete()
    return redirect(url_for('.lectures_admin'))

# Events
@admin.route("/events")
@admin.route("/events/<pk>", methods=["GET", "POST"])
@login_required
@admin_required
def events_admin(pk=None):
    if pk:
        event = Event.get(pk=pk)
        if not event:
            abort(404)
        if request.form:
            form = EventForm(request.form)
        else:
            form = EventForm(
                summary=event.summary,
                date=event.date,
                end_date=event.end_date,
                url=event.url,
            )
        if request.method == 'POST' and form.validate():
            event.summary = form.summary.data
            event.date = form.date.data
            event.end_date = form.end_date.data
            event.url = form.url.data
            event.save()
            return redirect(url_for('.events_admin'))
        return render_template('admin/events_edit.html', form=form, event=event)
    items_per_page = 12
    data = {"limit": items_per_page}
    try:
        page = int(request.args.get('page'))
    except ValueError:
        page = 1
    except TypeError:
        page = 1
    data["events_count"] = Event.count()
    total_pages = int(data["events_count"] / items_per_page + 0.99)
    if page:
        if page > total_pages:
            page = 1
    else:
        page = 1
    offset = (page - 1) * items_per_page
    data["events"] = Event.filter(limit=items_per_page, offset=offset)
    data["pagination"] = Paginator(current_page=page, total_pages=total_pages)
    return render_template("admin/events.html", **data)

@admin.route("/events/<pk>/delete", methods=["POST"])
@login_required
@admin_required
def events_delete(pk):
    try:
        event = Event.get(pk=int(pk))
    except Exception:
        event = None
    if not event:
        return abort(404)
    event.delete()
    return redirect(url_for('.events_admin'))
