from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from itupass.models import Lecture


class LectureForm(FlaskForm):
    """Form for Lectures."""
    name = StringField(
        _("Name"), validators=[Length(max=254)],
        render_kw={
            "placeholder": _("Lecture Name"),
            "class": "form-control"
        }
    )
    crn = StringField(
        _("CRN"), validators=[],
        render_kw={
            "placeholder": _("CRN Code"),
            "class": "form-control"
        }
    )
    code = StringField(
        _("Code"), validators=[Length(max=10)],
        render_kw={
            "placeholder": _("Lecture Code"),
            "class": "form-control"
        }
    )
    instructor = StringField(
        _("Name"), validators=[Length(max=254)],
        render_kw={
            "placeholder": _("Name Surname"),
            "class": "form-control"
        }
    )
    year = StringField(
        _("Year"), validators=[],
        render_kw={
            "placeholder": _("Registration year for Lecture"),
            "class": "form-control"
        }
    )

    def validate_crn(self, field):
        try:
            field.data = int(field.data)
        except:
            raise ValidationError(_("CRN should be integer."))

    def validate_year(self, field):
        try:
            field.data = int(field.data)
        except:
            raise ValidationError(_("Year should be integer."))
