from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from itupass.models import User
from itupass import SUPPORTED_LANGUAGES


class UserForm(FlaskForm):
    """Form for user."""
    name = StringField(
        _("Name"), validators=[Length(max=199)],
        render_kw={
            "placeholder": _("Name Surname"),
            "class": "form-control"
        }
    )
    email = EmailField(
        _("Email"), validators=[DataRequired(), Email()],
        render_kw={
            "placeholder": _("Email: @itu.edu.tr"),
            "class": "form-control"
        }
    )
    department = SelectField(
        _("Department"), validators=[DataRequired()],
        choices=[]
    )


class UserRegistrationForm(UserForm):
    """Registration form for user."""
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

    def validate_email(self, field):
        """Check for university email domain."""
        if '@itu.edu.tr' not in field.data:
            raise ValidationError(_("Sorry, you can only register using ITU email address."))
        if User.get(email=field.data):
            raise ValidationError(_("Sorry, user with this email address is already registered."))


class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField(
        _("Email"), validators=[DataRequired(), Length(min=4, max=49)],
        render_kw={
            "placeholder": _("E-mail"),
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


class UserAdminForm(UserForm):
    deleted = BooleanField(
        _("Deleted")
    )
    is_teacher = BooleanField(
        _("Teacher")
    )
    is_staff = BooleanField(
        _("Staff")
    )
    locale = SelectField(
        _("Language"), validators=[DataRequired()],
        choices=[(key, SUPPORTED_LANGUAGES[key]) for key in SUPPORTED_LANGUAGES]
    )

    def validate_locale(self, field):
        if field.data not in SUPPORTED_LANGUAGES:
            raise ValidationError(_("Locale is not defined in settings."))
