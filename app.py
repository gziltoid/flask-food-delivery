import csv
import os
import sys

from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, redirect, url_for, request, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_wtf.form import FlaskForm
from sqlalchemy import func
from wtforms.fields.core import StringField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields.simple import SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

load_dotenv(find_dotenv())

app = Flask(__name__)
csrf = CSRFProtect(app)

DB_URI = os.getenv("DATABASE_URL")
if DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)

app.config.update(
    DEBUG=True,
    SQLALCHEMY_ECHO=False,
    SECRET_KEY=os.getenv("SECRET_KEY"),
    SQLALCHEMY_DATABASE_URI=DB_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
app.debug = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)

categories_dishes_association = db.Table(
    "categories_dishes",
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id")),
    db.Column("dish_id", db.Integer, db.ForeignKey("dishes.id")),
)

orders_dishes_association = db.Table(
    "orders_dishes",
    db.Column("order_id", db.Integer, db.ForeignKey("orders.id")),
    db.Column("dish_id", db.Integer, db.ForeignKey("dishes.id")),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    # address = db.Column(db.String, nullable=False)
    orders = db.relationship("Order", back_populates="user")

    def __repr__(self):
        return self.mail


class Dish(db.Model):
    __tablename__ = "dishes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer)
    description = db.Column(db.Text)
    picture = db.Column(db.String)
    categories = db.relationship(
        "Category", secondary=categories_dishes_association, back_populates="dishes"
    )
    orders = db.relationship(
        "Order", secondary=orders_dishes_association, back_populates="dishes"
    )

    def __repr__(self):
        return self.title


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    dishes = db.relationship(
        "Dish", secondary=categories_dishes_association, back_populates="categories"
    )

    def __repr__(self):
        return self.title


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=func.now())
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    mail = db.Column(db.String, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String, nullable=False)
    dishes = db.relationship(
        "Dish", secondary=orders_dishes_association, back_populates="orders"
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="orders")

    def __repr__(self):
        return str(self.id)


class UserView(ModelView):
    column_list = ['mail', 'orders']
    column_searchable_list = ['mail']
    column_filters = ['mail']

    page_size = 20


class DishView(ModelView):
    column_list = ['title', 'categories', 'price', 'description']
    column_searchable_list = ['title', 'description', 'price']
    column_filters = ['title', 'description']
    column_sortable_list = ['title', 'price']

    page_size = 20


class CategoryView(ModelView):
    column_list = ['title', 'dishes']
    column_searchable_list = ['title']
    column_filters = ['title']


class OrderView(ModelView):
    column_list = ['date', 'user', 'status', 'total', 'dishes', 'phone', 'address']
    column_sortable_list = ['date', ('user', 'user.mail'), 'status', 'total']
    column_searchable_list = ['status', 'phone', 'address']
    page_size = 25


admin = Admin(app)

admin.add_view(UserView(User, db.session, name='Пользователи'))
admin.add_view(DishView(Dish, db.session, name='Блюда'))
admin.add_view(CategoryView(Category, db.session, name='Категории блюд'))
admin.add_view(OrderView(Order, db.session, name='Заказы'))


class LoginForm(FlaskForm):
    email = EmailField(
        "Электропочта", [DataRequired(), Email(message="Неверный формат почты")]
    )
    password = PasswordField("Пароль",
                             [DataRequired(), Length(min=8, message="Пароль должен быть не менее 8 символов")])
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    email = EmailField(
        "Электропочта", [DataRequired(), Email(message="Неверный формат почты")])
    password = PasswordField("Пароль",
                             [DataRequired(),
                              Length(min=8, message="Пароль должен быть не менее 8 символов"),
                              EqualTo("confirm_password", message="Пароли не совпадают")])
    confirm_password = PasswordField("Повторите пароль", [DataRequired()])
    submit = SubmitField("Зарегистрироваться")


class OrderForm(FlaskForm):
    name = StringField(
        "Ваше имя", [DataRequired(), Length(max=50, message="Слишком длинное имя")]
    )
    address = StringField(
        "Адрес", [DataRequired(), Length(max=200, message="Слишком длинный адрес")]
    )
    email = EmailField(
        "Электропочта", [DataRequired(), Email(message="Неверный формат почты")]
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


def load_data_from_csv(filename):
    try:
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = []
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        sys.exit("Error: CSV file is not found.")
    else:
        return data


@app.cli.command("seed")
def seed():
    """ Add seed data to the database. """
    categories = load_data_from_csv("db-seed-data/delivery_categories.csv")
    dishes = load_data_from_csv("db-seed-data/delivery_items.csv")

    for cat in categories:
        db.session.add(Category(title=cat["title"]))
    db.session.commit()

    for d in dishes:
        dish = Dish(
            title=d["title"],
            price=d["price"],
            description=d["description"],
            picture=d["picture"]
        )
        cat = Category.query.filter(Category.id == d["category_id"]).one()
        dish.categories.append(cat)
        db.session.add(dish)
    db.session.commit()


@app.route("/", methods=["GET", "POST"])
def index_view():
    # session.clear()
    categories = Category.query.all()

    if request.method == "POST":
        cart = session.get("cart", [])
        dish_id = int(request.form.get('dish'))
        cart.append(dish_id)
        session['cart'] = cart
        # TODO flash()
        return redirect(url_for('cart_view'))

    return render_template("main.html", categories=categories)


@app.route("/cart/", methods=["GET", "POST"])
def cart_view():
    form = OrderForm()
    if form.validate_on_submit():
        # FIXME check email
        user = User.query.get_or_404(session.get('user_id'), "The user is not found.")
        order = Order(
            phone=form.phone.data,
            address=form.address.data,
            mail=form.email.data,
            total=request.form.get('order_summ'),
            status='Принято',
            user_id=user.id
        )
        cart = session.get("cart", [])
        for item_id in cart:
            dish = Dish.query.get_or_404(item_id, "The dish is not found.")
            order.dishes.append(dish)
        # TODO order.save()
        db.session.add(order)
        db.session.commit()
        session.pop("cart")
        return redirect(url_for('ordered_view'))

    return render_template("cart.html", form=form)


@app.route("/ordered/")
def ordered_view():
    return render_template("ordered.html")


@app.route("/account/")
def account_view():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index_view'))

    orders = User.query.get_or_404(user_id).orders
    return render_template("account.html", orders=orders)


@app.route("/register/", methods=["GET", "POST"])
def register_view():
    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user_exists = User.query.filter_by(mail=email).one_or_none()
        if user_exists:
            form.email.errors.append("Такой пользователь уже существует.")
        else:
            user = User(mail=email, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login_view'))

    return render_template("register.html", form=form)


@app.route("/login/", methods=["GET", "POST"])
def login_view():
    if session.get("user_id"):
        return redirect(url_for('account_view'))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(mail=email).one_or_none()
        if not user:
            form.email.errors.append("Такого пользователя не существует.")
        elif user.password != password:
            form.password.errors.append("Неверный пароль.")
        else:
            session["user_id"] = user.id
            return redirect(url_for('index_view'))

    return render_template("login.html", form=form)


@app.route("/logout/")
def logout_view():
    if session.get("user_id"):
        session.pop("user_id")
    return redirect(url_for("login_view"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", error=error), 404


@app.errorhandler(500)
def page_server_error(error):
    return f"Something happened but we're fixing it: {error}", 500


if __name__ == "__main__":
    app.run()
