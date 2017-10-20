from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError


class UserForm(FlaskForm):
    """Registration form for user."""
    username = StringField(
        _("Username"), validators=[DataRequired(), Length(min=4, max=49)],
        render_kw={
            "placeholder": _("Username"),
            "class": "form-control"
        }
    )
    email = EmailField(
        _("Email"), validators=[DataRequired(), Email()],
        render_kw={
            "placeholder": _("@itu.edu.tr"),
            "class": "form-control"
        }
    )
    password = PasswordField(
        _("Password"), validators=[DataRequired(), EqualTo('confirm', message=_("Passwords must match!"))],
        render_kw={
            "placeholder": _("Password"),
            "class": "form-control"
        }
    )
    confirm = PasswordField(
        _("Repeat Password"),
        render_kw={
            "placeholder": _("Confirm Password"),
            "class": "form-control"
        }
    )
    name = StringField(
        _("Name"), validators=[Length(max=199)],
        render_kw={
            "placeholder": _("Name Surname"),
            "class": "form-control"
        }
    )
    is_teacher = SelectField(
        _("Role"), choices=[(False, _("Student")), (True, _("Teacher"))],
        render_kw={
            "class": "select2"
        }
    )

    def validate_email(form, field):
        if '@itu.edu.tr' not in field.data:
            raise ValidationError(_("Sorry, you can only register using ITU email address."))


class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField(
        _("Username"), validators=[DataRequired(), Length(min=4, max=49)],
        render_kw={
            "placeholder": _("Username"),
            "class": "form-control"
        }
    )
    password = PasswordField(
        _("Password"), validators=[DataRequired()],
        render_kw={
            "placeholder": _("Password"),
            "class": "form-control"
        }
    )
