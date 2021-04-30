from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route("/")
def index_view():
    return render_template("main.html")


@app.route("/cart/")
def cart_view():
    return render_template("cart.html")


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
