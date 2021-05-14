from flask_admin.contrib.sqla import ModelView

from food_delivery.models import db, User, Dish, Category, Order


class UserView(ModelView):
    column_list = ["email", "name", "orders"]
    column_searchable_list = ["email", "name"]
    column_filters = ["email", "name"]
    page_size = 20


class DishView(ModelView):
    column_list = ["title", "price", "description", "categories"]
    column_searchable_list = ["title", "description", "price"]
    column_filters = ["title", "description"]
    column_sortable_list = ["title", "price"]
    page_size = 20


class CategoryView(ModelView):
    column_list = ["title", "dishes"]
    column_searchable_list = ["title"]
    column_filters = ["title"]


class OrderView(ModelView):
    column_list = ["date", "user", "total", "dishes", "phone", "address", "status"]
    column_sortable_list = ["date", ("user", "user.email"), "total"]
    column_filters = ["phone", "address"]
    column_searchable_list = ["phone", "address"]
    page_size = 25


def init_admin(admin):
    admin.add_view(UserView(User, db.session, name="Пользователи"))
    admin.add_view(DishView(Dish, db.session, name="Блюда"))
    admin.add_view(CategoryView(Category, db.session, name="Категории блюд"))
    admin.add_view(OrderView(Order, db.session, name="Заказы"))
