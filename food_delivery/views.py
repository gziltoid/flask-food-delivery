from flask import (
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    abort,
)
from flask_admin.helpers import is_safe_url
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)

from food_delivery import app
from food_delivery.forms import LoginForm, RegistrationForm, OrderForm
from food_delivery.models import User, Dish, Order, Category


@app.before_request
def admin_access():
    if "admin" in request.url:
        if not (current_user.is_authenticated and current_user.is_admin):
            return redirect(url_for("login_view"))


@app.route("/", methods=["GET", "POST"])
def index_view():
    categories = Category.query.all()

    if request.method == "POST":
        cart = session.get("cart", {"items": [], "total": 0})
        dish_id = int(request.form.get("dish_id"))
        if dish_id not in cart.get("items"):
            cart["items"].append(dish_id)
            cart["total"] += Dish.query.get(dish_id).price
            session["cart"] = cart
            return redirect(url_for("index_view"))

    return render_template("main.html", categories=categories)


@app.route("/cart/", methods=["GET", "POST"])
def cart_view():
    cart = session.get("cart", {"items": [], "total": 0})
    cart_items = []
    for item_id in cart.get("items"):
        cart_items.append(Dish.query.get(item_id))

    form = OrderForm()

    if form.validate_on_submit() and cart_items:
        user = User.query.get(current_user.id)
        order = Order(
            phone=form.phone.data,
            address=form.address.data,
            total=sum(cart_item.price for cart_item in cart_items),
            user_id=user.id,
        )
        for item_id in cart.get("items"):
            dish = Dish.query.get(item_id)
            order.dishes.append(dish)
        order.save()
        session.pop("cart", None)
        return redirect(url_for("ordered_view"))

    return render_template("cart.html", form=form, cart=cart_items)


@app.route("/delete-from-cart/", methods=["POST"])
def delete_from_cart_view():
    dish_id = int(request.form.get("dish_id"))
    cart = session.get("cart", {"items": [], "total": 0})
    cart.get("items").remove(dish_id)
    cart["total"] -= Dish.query.get(dish_id).price
    session["cart"] = cart
    flash("Блюдо удалено из корзины", "warning")
    return redirect(url_for("cart_view"))


@app.route("/ordered/")
@login_required
def ordered_view():
    return render_template("ordered.html")


@app.route("/account/")
@login_required
def account_view():
    orders = User.query.get_or_404(current_user.id).orders
    return render_template("account.html", orders=orders)


@app.route("/register/", methods=["GET", "POST"])
def register_view():
    if current_user.is_authenticated:
        return redirect(url_for("account_view"))

    form = RegistrationForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        user_exists = User.query.filter_by(email=email).one_or_none()
        if user_exists:
            form.email.errors.append("Такой пользователь уже существует.")
        else:
            user = User(name=name, email=email, password=password)
            user.save()
            login_user(user)
            next_ = request.args.get("next")
            if next_ and not is_safe_url(next_):
                return abort(400)
            return redirect(next_ or url_for("account_view"))

    return render_template("register.html", form=form)


@app.route("/login/", methods=["GET", "POST"])
def login_view():
    if current_user.is_authenticated:
        return redirect(url_for("account_view"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).one_or_none()
        if not user:
            form.email.errors.append("Такого пользователя не существует.")
        elif not user.password_valid(password):
            form.password.errors.append("Неверный пароль.")
        else:
            login_user(user)
            if current_user.is_admin:
                return redirect("/admin")
            next_ = request.args.get("next")
            if next_ and not is_safe_url(next_):
                return abort(400)
            return redirect(next_ or url_for("index_view"))

    return render_template("login.html", form=form)


@app.route("/logout/")
def logout_view():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("login_view"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error=error, message='Страница не найдена'), 404


@app.errorhandler(500)
def page_server_error(error):
    return render_template("error.html", error=error, message='Мы уже работаем над этим'), 500