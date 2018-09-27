from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

import os

if os.environ.get("HEROKU"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    # three slashes mean that the file is in the same folder where all
    # the application's files are
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hoax.db"
    # configure SQLAlchemy to print all SQL queries
    app.config["SQLALCHEMY_ECHO"] = True
# disable a deprecated option
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# object which we use to access the database
db = SQLAlchemy(app)

from application import views

from application.auth import views

from application.communities import models
from application.communities import views

from application.accounts import models
from application.accounts import views

from application.accounts.models import Account
from os import urandom
app.config["SECRET_KEY"] = urandom(32)

from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth_login"
login_manager.login_message = "please login to use this functionality"

@login_manager.user_loader
def load_account(account_id):
    return Account.query.get(account_id)

try:
    db.create_all()
except:
    pass
