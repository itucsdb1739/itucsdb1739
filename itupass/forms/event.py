from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, ValidationError
from itupass.models import Event


class EventForm(FlaskForm):
    """Form for Events."""
    summary = StringField(
        _("Summary"), validators=[Length(max=200)],
        render_kw={
            "placeholder": _("Event Summary"),
            "class": "form-control"
        }
    )
    date = StringField(
        _("Date"), validators=[],
        render_kw={
            "placeholder": _("Event Date"),
            "class": "form-control"
        }
    )
    end_date = StringField(
        _("Turkish Translation"), validators=[],
        render_kw={
            "placeholder": _("End Date for Event"),
            "class": "form-control"
        }
    )
    url = StringField(
        _("URL"), validators=[Length(max=200)],
        render_kw={
            "placeholder": _("Event URL"),
            "class": "form-control"
        }
    )
