from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_user, login_required, logout_user, current_user
from itupass.models import Paginator, Department, User, Lecture, EventCategory, Event
from itupass.forms import UserAdminForm
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
