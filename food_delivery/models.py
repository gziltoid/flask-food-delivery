from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy_utils import ChoiceType
from werkzeug.security import generate_password_hash, check_password_hash

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


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    orders = db.relationship("Order", back_populates="user")
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def password(self):
        raise AttributeError("Prohibited")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def password_valid(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return self.email


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


OrderStatusType = [
    ("New", "Новый"),
    ("Processing", "Обрабатывается"),
    ("Completed", "Выполнен"),
]


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=func.now(), nullable=False)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(ChoiceType(OrderStatusType), nullable=False, default="New")
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String, nullable=False)
    dishes = db.relationship(
        "Dish", secondary=orders_dishes_association, back_populates="orders"
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="orders")

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return str(self.id)
