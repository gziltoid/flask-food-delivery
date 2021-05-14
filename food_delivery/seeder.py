import csv
import sys

from food_delivery.models import db, Category, Dish
from food_delivery import app


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


@app.cli.command("seed")
def seed():
    """ Add seed data to the database. """
    categories = load_data_from_csv("food_delivery/db-seed-data/delivery_categories.csv")
    dishes = load_data_from_csv("food_delivery/db-seed-data/delivery_items.csv")

    for cat in categories:
        db.session.add(Category(title=cat["title"]))
    db.session.commit()

    for d in dishes:
        dish = Dish(
            title=d["title"],
            price=d["price"],
            description=d["description"],
            picture=d["picture"],
        )
        cat = Category.query.filter(Category.id == d["category_id"]).one()
        dish.categories.append(cat)
        db.session.add(dish)
    db.session.commit()
