import csv
import os
import sys

from dotenv import load_dotenv, find_dotenv
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from views import app

load_dotenv(find_dotenv())

DB_URI = os.getenv("DATABASE_URL")
if DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)

app.config.update(
    DEBUG=False,
    SQLALCHEMY_ECHO=False,
    SECRET_KEY=os.getenv("SECRET_KEY"),
    SQLALCHEMY_DATABASE_URI=DB_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

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
    order_date = db.Column(db.String, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    mail = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String, nullable=False)
    dishes = db.relationship(
        "Dish", secondary=orders_dishes_association, back_populates="orders"
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="orders")


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
            description=d["title"],
            picture=d["title"]
        )
        cat = Category.query.filter(Category.id == d["category_id"]).one()
        dish.categories.append(cat)
        db.session.add(dish)
    db.session.commit()


if __name__ == "__main__":
    app.run()
