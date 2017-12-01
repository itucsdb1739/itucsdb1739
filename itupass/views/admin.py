from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from itupass.models import Department, User, Lecture, EventCategory, Event

admin = Blueprint('admin', __name__)


@admin.route("/")
@login_required
def admin_index():
    if not current_user.is_staff:
        return redirect(url_for('client.index'))
    current_year = datetime.now().year
    data = {}
    data["users_count"] = User.count(deleted=False)
    data["lectures_count"] = Lecture.count(year=current_year+1)
    data["departments_count"] = Department.count()
    data["event_cats_count"] = EventCategory.count()
    data["events_count"] = Event.count()
    return render_template("admin/index.html", **data)

@admin.route("/users")
@login_required
def users_admin(pk=None):
    items_per_page = 25
    data = {"limit": items_per_page}
    try:
        page = int(request.args.get('page'))
    except ValueError:
        page = 1
    if pk:
        pass
    data["users_count"] = User.count(deleted=False)
    data["pages"] = int(data["users_count"] / items_per_page + 0.99)
    if page:
        if (page-1) * items_per_page > data["users_count"]:
            page = 1
    else:
        page = 1
    data["current_page"] = page
    offset = (page - 1) * items_per_page
    data["users"] = User.filter(limit=items_per_page, offset=offset)
    return render_template("admin/users.html", **data)
