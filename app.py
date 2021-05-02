import csv
import os
import sys

from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, redirect, url_for, request
from flask.globals import session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_wtf.form import FlaskForm
from sqlalchemy import func
from wtforms.fields.core import StringField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, Email

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


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    dishes = db.relationship(
        "Dish", secondary=categories_dishes_association, back_populates="categories"
    )


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=func.now())
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
    categories = Category.query.all()

    if request.method == "POST":
        cart = session.get("cart", [])
        dish_id = int(request.form.get('dish'))
        cart.append(dish_id)
        session["user_id"] = 1
        session['cart'] = cart
        # TODO flash()
        # print(session['cart'])
        return redirect(url_for('cart_view'))

    return render_template("main.html", categories=categories)


@app.route("/cart/", methods=["GET", "POST"])
def cart_view():
    print(session.get("cart"))

    form = OrderForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(session["user_id"], "The user is not found.")
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
        return redirect(url_for('ordered_view'))

    return render_template("cart.html", form=form)


@app.route("/ordered/")
def ordered_view():
    return render_template("ordered.html")


@app.route("/account/")
def account_view():
    return render_template("account.html")


@app.route("/register/")
def register_view():
    return render_template("register.html")


@app.route("/auth/")
def auth_view():
    return render_template("auth.html")


@app.route("/login/")
def login_view():
    return render_template("login.html")


@app.route("/logout/")
def logout_view():
    return redirect(url_for("auth_view"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", error=error), 404


@app.errorhandler(500)
def page_server_error(error):
    return f"Something happened but we're fixing it: {error}", 500


if __name__ == "__main__":
    app.run()
