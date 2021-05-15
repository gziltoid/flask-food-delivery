import csv
import sys

from food_delivery.models import db, Category, Dish


def load_data_from_csv(filename):
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = []
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        sys.exit("Error: CSV file is not found.")
    else:
        return data


def seed():
    """ Add seed data to the database. """
    categories = load_data_from_csv("./db-seed-data/delivery_categories.csv")
    dishes = load_data_from_csv("./db-seed-data/delivery_items.csv")

    for c in categories:
        db.session.add(Category(title=c["title"]))
    db.session.commit()

    for d in dishes:
        dish = Dish(
            title=d["title"],
            price=d["price"],
            description=d["description"],
            picture=d["picture"],
        )
        c = Category.query.filter(Category.id == d["category_id"]).one()
        dish.categories.append(c)
        db.session.add(dish)
    db.session.commit()
