from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,DateField, TimeField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class RegisterForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6)]
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password")]
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Login")

class OrderForm(FlaskForm):
    event_date = DateField(
        "Event date",
        validators=[DataRequired()]
    )

    event_time = TimeField(
        "Event time",
        validators=[DataRequired()]
    )

    address = StringField(
        "Address",
        validators=[DataRequired(), Length(max=255)]
    )

    guests_count = IntegerField(
        "Guests count",
        validators=[DataRequired()]
    )
    
    phone = StringField("Телефон", validators=[DataRequired(), Length(max=20)])
    client_comment = TextAreaField("Комментарий к заказу", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Place order")