import csv
import sys

from flask import Flask
from flask_admin import Admin
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from food_delivery.admin import init_admin
from food_delivery.config import Config
from food_delivery.models import db


app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

admin_manager = Admin()
admin_manager.init_app(app)
init_admin(admin_manager)

from food_delivery.views import *
from food_delivery import filters

login_manager = LoginManager(app)
login_manager.login_view = "login_view"
login_manager.login_message_category = "warning"
login_manager.login_message = "Авторизуйтесь для доступа к странице"


@login_manager.user_loader
def load_user(uid):
    return User.query.get(uid)

@app.cli.command("seed")
def seed():
    from food_delivery.seeder import seed
    seed()

