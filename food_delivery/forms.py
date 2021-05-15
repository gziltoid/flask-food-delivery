from flask_wtf.form import FlaskForm
from wtforms.fields.core import StringField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields.simple import SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    email = EmailField(
        "Почта", [DataRequired(), Email(message="Неверный формат почты")]
    )
    password = PasswordField(
        "Пароль",
        [
            DataRequired(),
            Length(min=5, message="Пароль должен быть не менее 5 символов"),
        ],
    )
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    name = StringField(
        "Имя",
        [
            DataRequired(),
            Length(max=50, message="Имя должно быть не более 50 символов"),
        ],
    )
    email = EmailField(
        "Почта", [DataRequired(), Email(message="Неверный формат почты")]
    )
    password = PasswordField(
        "Пароль",
        [
            DataRequired(),
            Length(min=5, message="Пароль должен быть не менее 5 символов"),
            EqualTo("confirm_password", message="Пароли не совпадают"),
        ],
    )
    confirm_password = PasswordField("Повторите пароль", [DataRequired()])
    submit = SubmitField("Зарегистрироваться")


class OrderForm(FlaskForm):
    name = StringField(
        "Ваше имя", [DataRequired(), Length(max=50, message="Слишком длинное имя")]
    )
    address = StringField(
        "Адрес", [DataRequired(), Length(max=200, message="Слишком длинный адрес")]
    )
    phone = TelField(
        "Телефон",
        [
            DataRequired(),
            Length(
                min=10,
                max=15,
                message="Номер должен состоять из %(min)d-%(max)d символов",
            ),
        ],
    )
    submit = SubmitField("Оформить заказ")
