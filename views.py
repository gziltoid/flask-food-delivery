from flask import Flask, render_template, abort

app = Flask(__name__)


@app.route("/")
def index_view():
    pass


@app.route("/cart/")
def cart_view():
    pass


@app.route("/account/")
def account_view():
    pass


@app.route("/login/")
def login_view():
    pass


@app.route("/logout/")
def logout_view():
    pass


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", error=error), 404


@app.errorhandler(500)
def page_server_error(error):
    return f"Something happened but we're fixing it: {error}", 500
