from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    name = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
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
    dishes = db.relationship(
        "Dish", secondary=orders_dishes_association, back_populates="orders"
    )
